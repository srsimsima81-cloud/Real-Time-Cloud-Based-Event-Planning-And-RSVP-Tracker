from app.services.analytics import event_analytics
import pytest

def test_basic_math():
    assert round(350/500*100,2)==70.0
    assert max(100-99,0)==1

@pytest.mark.asyncio
async def test_analytics_empty():
    class FakeResult:
        def all(self): return []
    class FakeDB:
        async def execute(self, *args, **kwargs): return FakeResult()
        async def scalar(self, *args, **kwargs): return 0
    data=await event_analytics(FakeDB(),1,100)
    assert data["going"]==0 and data["available_seats"]==100
