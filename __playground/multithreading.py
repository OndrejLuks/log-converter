def _run_output(interp, request, channels=None):
    script, rpipe = _captured_script(request)
    with rpipe:
        interp.run(script, channels=channels)
        return rpipe.read()

# Example object to pass
person = {
    "name": "Alice",
    "age": 30
}

# Example code template with placeholders for object representation
code_template = """
def process_person(person_data):
    print("Name:", person_data['name'])
    print("Age:", person_data['age'])

person_data = {object_representation}
process_person(person_data)
"""

# Format the code template with the object's representation
formatted_code = code_template.format(object_representation=repr(person))

# Call the _run_output function with the formatted code
output = _run_output(interpreter_instance, formatted_code)
print("Output:", output)