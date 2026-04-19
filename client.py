import json
import socket
from typing import Dict
from urllib.parse import urlparse


class HTTPResponse:
    def __init__(self, raw_response: bytes):
        self.raw = raw_response
        self.status_code = 0
        self.status_message = ""
        self.headers = {}
        self.body = ""
        self.cookies = {}
        self.parse_response()

    def parse_response(self):
        try:
            # split the headers and the body
            header_end = self.raw.find(b"\r\n\r\n")
            # we didnt find the header, return nothing
            if header_end == -1:
                return

            headers_section = self.raw[:header_end].decode("utf-8", errors="ignore")
            body_section = self.raw[header_end + 4 :]

            # parse status code and message line
            lines = headers_section.split("\r\n")
            if lines:
                status_line = lines[0]
                parts = status_line.split(" ", 2)
                if len(parts) >= 2:
                    self.status_code = int(parts[1])
                    self.status_message = parts[2] if len(parts) > 2 else ""

            # parse the headers
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    self.headers[key.strip().lower()] = value.strip()

            # parse the cookies
            if "set-cookie" in self.headers:
                self.parse_cookies(self.headers["set-cookie"])

            self.body = body_section.decode("utf-8", errors="ignore")

        except Exception as e:
            print(f"error parssing response: {e}")

    def parse_cookies(self, cookie_header: str):
        # this is a very simplified implementation of cookies
        # it will not work for many responses
        parts = cookie_header.split(";")

        if parts:
            cookie_pair = parts[0].strip()

            if "=" in cookie_pair:
                name, value = cookie_pair.split("=", 1)
                self.cookies[name.strip()] = value.strip()

    def json(self) -> dict:
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return {}


# **note that the client does not support HTTPS
class HttpClient:
    def __init__(self):
        self.cookies = {}
        self.default_headers = {
            "User-Agent": "HttpClient/1.0",
            "Accept": "*/*",
            "Connection": "close",
        }

    def create_socket(self, host: str, port: int) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        sock.connect((host, port))
        return sock

    def build_request(self, method: str, path: str, host: str, headers, body) -> str:
        request_lines = [f"{method} {path} HTTP/1.1"]

        request_lines.append(f"Host: {host}")

        # add our default headers
        all_headers = self.default_headers.copy()
        if headers:
            all_headers.update(headers)

        # add any cookies if we have any
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            all_headers["Cookie"] = cookie_str

        if body:
            all_headers["Content-Length"] = str(len(body.encode("utf-8")))

        for key, value in all_headers.items():
            request_lines.append(f"{key}: {value}")

        # end teh headers section
        request_lines.append("\r\n")

        # add the body if needed
        request = "\r\n".join(request_lines)
        if body:
            request += body

        return request

    def send_request(
        self, url: str, method: str = "GET", headers=None, data=None, json_data=None
    ) -> HTTPResponse:
        parsed = urlparse(url)
        host = parsed.hostname

        if not host:
            raise ValueError("Invalid host")

        port = parsed.port
        path = parsed.path or "/"

        if parsed.query:
            path += f"?{parsed.query}"

        # default to 80 since we don't support HTTPS
        # if 443 is tried it won't work since we don't have any SSL
        if port is None:
            port = 80

        req_headers = headers.copy() if headers else {}

        body = None

        if json_data:
            body = json.dumps(json_data)
            req_headers["Content-Type"] = "application/json"
        elif data:
            # simple form encoding
            body = "&".join([f"{k}={v}" for k, v in data.items()])
            req_headers["Content-Type"] = "application/x-www-form-urlencoded"

        request = self.build_request(method, path, host, req_headers, body)

        # send our request
        sock = self.create_socket(host, port)
        try:
            sock.sendall(request.encode("utf-8"))

            # receive and collect all chunks
            response_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            # parse the response
            response = HTTPResponse(response_data)

            # update the cookies
            if response.cookies:
                self.cookies.update(response.cookies)

            return response

        finally:
            # close the socket regardless of success or errors
            sock.close()

    def get(self, url: str, headers=None) -> HTTPResponse:
        return self.send_request(url, "GET", headers)

    def post(
        self,
        url: str,
        headers=None,
        data=None,
        json=None,
    ) -> HTTPResponse:
        return self.send_request(url, "POST", headers, data, json)

    def set_cookie(self, name: str, value: str):
        self.cookies[name] = value

    def get_cookies(self) -> Dict[str, str]:
        return self.cookies.copy()
