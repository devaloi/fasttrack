import pytest

from fasttrack.utils.pagination import decode_cursor, encode_cursor


@pytest.mark.asyncio
async def test_cursor_encode_decode():
    cursor = encode_cursor(42)
    assert decode_cursor(cursor) == 42


@pytest.mark.asyncio
async def test_invalid_cursor():
    with pytest.raises(ValueError, match="Invalid cursor"):
        decode_cursor("not-valid-base64!!!")


@pytest.mark.asyncio
async def test_cursor_round_trip():
    for i in [1, 100, 999999]:
        assert decode_cursor(encode_cursor(i)) == i
