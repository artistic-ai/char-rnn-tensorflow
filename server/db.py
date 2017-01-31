import aioredis


async def connect_to_redis(app):
    app.logger.info('Connecting to redis')
    app['redis']['connection'] = await aioredis.create_redis(
        (app['redis']['host'], app['redis']['port']),
        encoding='utf-8', db=app['redis']['db']
    )


async def close_redis(app):
    app.logger.info('Closing redis')
    app['redis']['connection'].close()


async def add_sample(sample, app):
    await app['redis']['connection'].rpush(app['redis']['generations_key'], sample)


async def get_samples(app):
    count = await app['redis']['connection'].llen(app['redis']['generations_key'])
    samples = await app['redis']['connection'].lrange(app['redis']['generations_key'], 0, count - 1)
    return [{
                'index': i,
                'text': samples[i]
            } for i in range(len(samples))]
