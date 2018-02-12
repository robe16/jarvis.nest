def check_redirect(r):
    if len(r.history) > 0:
        if r.history[0].is_redirect:
            return r.url
    return False