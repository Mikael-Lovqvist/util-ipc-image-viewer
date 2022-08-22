import io
from application_types import semantic_version


test = io.BytesIO()

semantic_version(1, 2, 3)._write(test)

print(test.getvalue())

test.seek(0)
v = semantic_version._read(test)

print(v)


print(semantic_version(1, 2, 3) == semantic_version(1, 2, 3))