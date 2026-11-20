import asyncio
import edge_tts

async def main():
    vs = await edge_tts.list_voices()
    for v in vs:
        if v["Locale"].startswith("de"):
            print(v["ShortName"], v["Gender"])

asyncio.run(main())
