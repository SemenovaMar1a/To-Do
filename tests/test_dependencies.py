from unittest.mock import MagicMock, patch

import pytest

from dependencies import get_current_user
from main import app

@pytest.mark.asyncio
async def test_get_current_user():
    fake_session = MagicMock()

    fake_token = "test.jwt.token"

    
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "testuser"}

        with patch("dependencies.get_user") as mock_get_user:
            mock_get_user.return_value = {"username": "testuser"}

            user = await get_current_user(fake_session, fake_token)

            assert user["username"] == "testuser"




    
