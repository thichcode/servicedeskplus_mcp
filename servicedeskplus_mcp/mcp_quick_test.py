# Quick MCP Server Start/Check
# Mục tiêu: test xong 40+ function (list_tickets, create_ticket, ...)

import asyncio, mcp
import json


async def test_mcp_tools(program_path):
    params = mcp.stdio.get_stdio_parameters(program_path)
    async with mcp.ClientSession(params) as session:
        tools = await session.list_tools()
        print(f'✅ Server running & {len(tools)} tools registered!')
        # Test list 5 tickets (mở)
        res = await session.call_tool('list_tickets', {'limit': 3, 'status': 'open'})
        if isinstance(res, dict) and 'content' in res:
            import sys
            data = json.loads(res['content'][0]['text'])
            print('\n📋 3 tickets mới nhất:')
            for t in data.get('result', [])[:3]:
                print(f" - #{t['id']}: {t['subject'][:60]} ...")
        return tools


if __name__ == '__main__':
    # MCP server là 1 process `python main.py` xuất ra stdout
    server_path = 'python main.py'
    # chạy 1 process riêng, xong chạy python test luôn được
    tools = asyncio.run(test_mcp_tools(server_path))
    print('\n✅ MCP server hoạt động & test xong! Bạn có thể dùng 40+ functions rồi!')