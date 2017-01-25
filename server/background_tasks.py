import asyncio

from sample import load_model, restore_session, get_sample


def close_session(app):
    if app.get('tf_session', None):
        app['tf_session'].close()
        app['tf_session'] = None


def reload_session(app):
    close_session(app)
    app['tf_session'] = restore_session(app['model_dir'])


def get_sample_text(app):
    if app.get('model', None) and app.get('tf_session', None):
        return get_sample(app['model'], app['tf_session'])


async def model_updater(app):
    try:
        app['model'] = load_model(app['model_dir'])
        app['tf_session'] = None
        while True:
            reload_session(app)
            await asyncio.sleep(app['reload_model'])
    except asyncio.CancelledError:
        pass
    finally:
        close_session(app)


async def text_generator(app):
    try:
        while True:
            new_item = {
                'text': get_sample_text(app),
                'index': len(app['text_generations'])
            }
            # Add new item
            app['text_generations'].append(new_item)
            # Wait for next run
            await asyncio.sleep(app['reload_text'])
    except asyncio.CancelledError:
        pass
    finally:
        close_session(app)


async def start_background_tasks(app):
    app['model_updater'] = app.loop.create_task(model_updater(app))
    app['text_generator'] = app.loop.create_task(text_generator(app))


async def cleanup_background_tasks(app):
    app['model_updater'].cancel()
    await app['model_updater']
    app['text_generator'].cancel()
    await app['text_generator']