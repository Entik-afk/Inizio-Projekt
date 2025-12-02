import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("format", ["json", "csv", "xml"])
def test_search_download(format):
    response = client.post(
        "/search",
        data={"query": "python", "format": format}
    )

    # Test status code
    assert response.status_code == 200

    # Test Content-Type
    if format == "json":
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, list)
    elif format == "csv":
        assert "text/csv" in response.headers["content-type"]
        content = response.content.decode()
        assert "Title,Link,Snippet" in content

    elif format == "xml":
        assert "application/xml" in response.headers["content-type"]
        content = response.content.decode()
        assert "<results>" in content