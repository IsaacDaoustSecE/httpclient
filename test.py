# test our http client using httpbin and jsonplaceholder apis
from client import HttpClient


def main():
    client = HttpClient()

    # Test 1: JSOnPlaceholder GET
    print("\n[Test 1] JSONPlaceholder GET post")
    print("-" * 40)
    response = client.get("https://jsonplaceholder.typicode.com/posts/1")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Post title: {data.get('title')}")
    print(f"Post body: {data.get('body')[:50]}...")

    # Test 2: JSONPlaceholder POST
    print("\n[Test 2] JSONPlaceholder POST new post")
    print("-" * 40)
    new_post = {
        "title": "Test from our client",
        "body": "This is a test post",
        "userId": 1,
    }
    response = client.post("https://jsonplaceholder.typicode.com/posts", json=new_post)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Created post ID: {result.get('id')}")
    print(f"Response: {result}")

    # Test 3: HTTPBin Headers
    print("\n[Test 3] HTTPBin Custom headers")
    print("-" * 40)
    custom_headers = {"X-Custom-Header": "TestValue", "X-Client-Version": "1.0"}
    response = client.get("https://httpbin.org/headers", headers=custom_headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Headers received by server: {result.get('headers', {})}")

    # Test 4: HTTPBin User Agent
    print("\n[Test 4] HTTPBin User agent")
    print("-" * 40)
    response = client.get("https://httpbin.org/user-agent")
    print(f"Status: {response.status_code}")
    print(f"User-Agent: {response.json()}")

    # Test 5: HTTPBin JSON POST
    print("\n[Test 5] HTTPBin POST JSON data")
    print("-" * 40)
    test_json = {
        "name": "Isaac",
        "age": 30,
        "active": True,
        "tags": ["python", "http", "sockets"],
    }
    response = client.post("https://httpbin.org/post", json=test_json)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Data sent: {result.get('json')}")
    print(f"Content-Type: {result.get('headers', {}).get('Content-Type')}")

    # Test 6: HTTPBin Cookies
    print("\n[Test 6] HTTPBin Cookies")
    print("-" * 40)
    response = client.get("https://httpbin.org/cookies/set/testcookie/testvalue")
    print(f"Set cookie status: {response.status_code}")

    response = client.get("https://httpbin.org/cookies")
    print(f"Get cookies status: {response.status_code}")
    result = response.json()
    print(f"Cookies: {result.get('cookies')}")


if __name__ == "__main__":
    main()
