from servers.file_utils.json import update_entity_field_fn

# ambiance.vibe
entity_id = "2a98cbf2-4fec-45f9-92e8-298f55bfa93a"
field = "ambience.vibe"
value = "A palpable sense of tension and unease hangs on everything and everyone"

result = update_entity_field_fn(entity_id, field, value)
print(result)
