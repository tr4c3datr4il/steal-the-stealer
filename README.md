Automatically crawling stealer/c2 messages from its chat group with api key + chat id (both is required obviously :D)


- First, create `token_list.json` in `utils/` directory or you can modify the code to read it from any path you want, any name you love.

- Add token and chat id with `update_token.py` or you can manually do it with this format:

```json
{
    "bots": [
        {
            "token": "1234567890:AAAbbbb-ccCCddEEEEE",
            "chat_id": -3219874560,
            "status": "False",
            "family": "Example"
        },
        {
            "token": "1234567890:AAAbbbb-ccCCddEEEEE",
            "chat_id": -3219874560,
            "status": "False",
            "family": "Braodo"
        },
        {
            "token": "1234567890:AAAbbbb-ccCCddEEEEE",
            "chat_id": -3219874560,
            "status": "False",
            "family": "None"
        },
    ]
}
```

- Update the profile parser you need if it not in the `utils/parser.py` code. 

- Run the code.


### REFS:

- https://gist.github.com/painor/7e74de80ae0c819d3e9abcf9989a8dd6

- https://github.com/soxoj/telegram-bot-dumper