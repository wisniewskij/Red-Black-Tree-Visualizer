import sys
import pygame
import asyncio

from Visualizer import Visualizer

async def main():
    visualizer = Visualizer()
    await visualizer.run()

if __name__ == '__main__':
    asyncio.run(main())
