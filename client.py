import json


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
