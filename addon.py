#!/usr/bin/env python3
from __future__ import annotations
import asyncio
import resources.lib.undernextrap as undernextrap


async def main():
    async with undernextrap.UnderNexTrapAnimeFree() as unext_af:
        await unext_af()

if __name__ == '__main__':
    asyncio.run(main())
