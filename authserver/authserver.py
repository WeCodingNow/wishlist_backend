import asyncio
from functools import partial
from aio_pika import connect, IncomingMessage, Exchange, Message

import json
import jwt

from settings import settings, rabbit_settings

def grab_user_params(params) -> dict:
    query_params = {
        key: value for key, value in params.items() if key in settings['query_params']
    }

    return query_params

def make_jwt(json_body) -> bytes:
    token = jwt.encode(
        payload=grab_user_params(json_body),
        key=settings['secret'],
        algorithm='HS256'
    )

    return token

def generate_token(json_body) -> bytes:
    return make_jwt(json_body)

def check_sign(json_body) -> bool:
    return json_body[settings['signature_param_name']].encode() == make_jwt(json_body)

async def on_reg_message(exchange: Exchange, message: IncomingMessage):
    with message.process():
        query_dict = json.loads(message.body.decode())

        response = generate_token(query_dict)

        await exchange.publish(
            Message(
                body=response,
                correlation_id=message.correlation_id
            ),
            routing_key=message.reply_to
        )

        print('registration request complete')

async def on_auth_message(exchange: Exchange, message: IncomingMessage):
    with message.process():
        query_dict = json.loads(message.body.decode())

        response = str(check_sign(query_dict)).encode()

        await exchange.publish(
            Message(
                body=response,
                correlation_id=message.correlation_id
            ),
            routing_key=message.reply_to
        )

        print('authorization request complete')

async def main(loop):
    await asyncio.sleep(20)
    connection = await connect(**rabbit_settings, loop=loop)

    channel = await connection.channel()

    queues_handlers = {
        settings['reg_queue_name']: on_reg_message,
        settings['auth_queue_name']: on_auth_message,
    }

    for queue_type, message_handler in queues_handlers.items():
        queue = await channel.declare_queue(queue_type)
        await queue.consume(partial(message_handler, channel.default_exchange))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    print("Awaiting RPC requests")
    loop.run_forever()
