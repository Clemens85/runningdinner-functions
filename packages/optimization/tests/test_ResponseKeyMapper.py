from aws_adapter.ResponseKeyMapper import map_response_key

def test_map_response_key():
    """
    Test the get_response_key function to ensure it correctly derives the response key from the source key.
    """
    source_key = "optimization/admin123/456-request.json"
    expected_response_key = "optimization/admin123/456-response.json"
    
    response_key = map_response_key(source_key)
    
    assert response_key == expected_response_key, f"Expected {expected_response_key}, but got {response_key}"