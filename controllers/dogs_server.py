from flask import request, jsonify, Blueprint
from mongodb_connection_manager import MongoConnectionHolder
from datetime import datetime
import uuid

dogs_blueprint = Blueprint('dogs_data', __name__)

################################# POST #################################

# 1. Create a new dog data
@dogs_blueprint.route('/dogs_data', methods=['POST'])
def create_dog_data():
    """
    Create a new dog data
    ---
    parameters:
        - name: dog_data
          in: body
          required: true
          description: The dog data to create
          schema:
            id: dog_data
            required:
                - breed_name
                - gender
                - from_age
                - to_age
                - avg_height_min
                - avg_height_max
                - avg_weight_min
                - avg_weight_max
                - avg_drink
                - avg_food
                - pic_url
            properties:
                breed_name:
                    type: string
                    description: The name of the dog's breed
                gender:
                    type: string
                    description: Male or female
                from_age:
                    type: string
                    description: The start age of the health suggestions
                to_age:
                    type: string
                    description: The end age of the health suggestions
                avg_height_min:
                    type: string
                    description: The aevrage height of the dog
                avg_height_max:
                    type: string
                    description: The aevrage height of the dog
                avg_weight_min:
                    type: string
                    description: The average weight of the dog
                avg_weight_max:
                    type: string
                    description: The average weight of the dog
                avg_drink:
                    type: string
                    description: The average drinking recommended for the dog
                avg_food:
                    type: string
                    description: The average eating recommended for the dog
                pic_url:
                    type: string
                    description: URL of picture of the dog breed
    responses:
        201:
            description: The dog data was created successfully
        400:
            description: The request was invalid
        500:
            description: An error occurred while creating the dog data
    """
    data = request.json
    db = MongoConnectionHolder.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    # Check if the request is valid
    if not all(key in data for key in ['breed_name', 'gender', 'from_age', 'to_age', 'avg_height_min', 'avg_height_max', 'avg_weight_min', 'avg_weight_max','avg_drink','avg_food','pic_url']):
        return jsonify({"error": "Invalid request"}), 400

   # Ensure that double values are rounded to two decimal places
    try:
        numeric_fields = {
            'from_age': round(float(data['from_age']), 2),
            'to_age': round(float(data['to_age']), 2),
            'avg_height_min': round(float(data['avg_height_min']), 2),
            'avg_height_max': round(float(data['avg_height_max']), 2),
            'avg_weight_min': round(float(data['avg_weight_min']), 2),
            'avg_weight_max': round(float(data['avg_weight_max']), 2),
            'avg_drink': round(float(data['avg_drink']), 2),
            'avg_food': round(float(data['avg_food']), 2)
        }
    except ValueError:
        return jsonify({"error": "Invalid number format"}), 400
    
    gender = data['gender']
    if gender not in ['Male','Female']:
        return jsonify({"error" : "Gender must be Male or Female"}),400
    
    if numeric_fields['from_age'] > numeric_fields['to_age']:
        return jsonify({"error":"'from_age' must be smaller than 'to_age'"}),400
    
    if numeric_fields['avg_height_min'] > numeric_fields['avg_height_max']:
        return jsonify({"error":"'avg_height_min' must be smaller than 'avg_height_max'"}),400
    
    if numeric_fields['avg_weight_min'] > numeric_fields['avg_weight_max']:
        return jsonify({"error":"'avg_weight_min' must be smaller than 'avg_weight_max'"}),400

    package_collection = db[data['breed_name']]

    overlapping_data = package_collection.find_one({
        "gender": gender,
        "$and" : [
            {"from_age": {"$lt":numeric_fields['to_age']}, "to_age":{"$gt": numeric_fields['from_age']}}
            ]
        })
    
    if overlapping_data:
        return jsonify({"error": "Overlapping age range exists for this breed"}),400

    # Create the dog data item
    dog_data_item = {
        "_id": str(uuid.uuid4()),
        "breed_name": data['breed_name'],
        "gender": data['gender'],
        "from_age": numeric_fields['from_age'],
        "to_age": numeric_fields['to_age'],
        "avg_height_min":numeric_fields['avg_height_min'],
        "avg_height_max":numeric_fields['avg_height_max'],
        "avg_weight_min":numeric_fields['avg_weight_min'],
        "avg_weight_max":numeric_fields['avg_weight_max'],
        "avg_drink":numeric_fields['avg_drink'],
        "avg_food":numeric_fields['avg_food'],
        "pic_url": data['pic_url'],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # Insert the dog breed into the database
    package_collection.insert_one(dog_data_item)

    return jsonify({"message": "Dog data created successfully", '_id': dog_data_item['_id']}), 201

################################# GET #################################

# 2. Get All dogs' breeds
@dogs_blueprint.route('/dogs_data/breeds', methods=['GET'])
def get_all_dogs_breeds():
    """
    Retrieve a list of all dog breeds
    ---
    responses:
        200:
            description: Dogs' breeds retrieved successfully
        500:
            description: An error occurred while deleting the dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        breeds = db.list_collection_names()
        return jsonify(breeds),200
    except Exception as e:
        return jsonify({"error": str(e)}),500

# 3. Get dog data by ID
@dogs_blueprint.route('/dogs_data/<dog_id>', methods=['GET'])
def get_dog_data_by_id(dog_id):
    """
    Retrieve a dog data by its ID
    ---
    parameters:
        - name: dog_id
          in: path
          required: true
          description: The dog_id of the dog data to retrieve
    responses:
        200:
            description: Dog data retrieved successfully
        404:
            description: Dog data not found
        500:
            description: An error occurred while deleting the dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    try:
        for breed in db.list_collection_names():
            dog_data = db[breed].find_one({"_id": dog_id})
            if dog_data:
                return jsonify(dog_data),200
        return jsonify({"error": "Dog data not found"}),404
    except Exception as e:
        return jsonify({"error": str(e)}),500

# 4. Get specified dog data by breed and age reange
@dogs_blueprint.route('/dogs_data/<breed_name>/<gender>/<from_age>/<to_age>', methods=['GET'])
def get_dog_data_by_breed_and_age_range(breed_name,gender,from_age,to_age):
    """
    Get dog data by its breed and age range
    ---
    parameters:
        - name: breed_name
          in: path
          required: true
          description: The breed_name of the dog data to retrieve
        - name: gender
          in: path
          required: true
          description: The gender of the dog
        - name: from_age
          in: path
          required: true
          description: The from_age of the dog data to retrieve
        - name: to_age
          in: path
          required: true
          description: The to_age of the dog data to retrieve
    responses:
        200:
            description: Dog data retrieved successfully
        404:
            description: Dog data not found
        500:
            description: An error occurred while deleting the dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        package_collection = db[breed_name]
        dog_data = package_collection.find_one({"gender" : gender,"from_age":round(float(from_age),2),"to_age":round(float(to_age),2)})
        if dog_data:
            return jsonify(dog_data),200 
        return jsonify({"error":"No data found for this breed and age range"}),404
    except Exception as e:
        return jsonify({"error": str(e)}),500

# Get specified dog data by breed and age
@dogs_blueprint.route('/dogs_data/<breed_name>/<gender>/<age>', methods=['GET'])
def get_dog_data_by_breed_and_age(breed_name,gender,age):
    """
    Get dog data by its breed and age
    ---
    parameters:
        - name: breed_name
          in: path
          required: true
          description: The breed_name of the dog data to retrieve
        - name: gender
          in: path
          required: true
          description: The gender of the dog
        - name: age
          in: path
          required: true
          description: The age of the dog data to retrieve
    responses:
        200:
            description: Dog data retrieved successfully
        404:
            description: Dog data not found
        500:
            description: An error occurred while deleting the dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    try:
        age = round(float(age),2)
        package_collection = db[breed_name]
        dog_data = package_collection.find_one({
            "gender": gender,
            "from_age":{"$lte":age},
            "to_age":{"$gte":age}
        })
        if dog_data:
            return jsonify(dog_data),200
        return jsonify({"error":"No data found for this breed and age"}),404
    except Exception as e:
        return jsonify({"error": str(e)}),500

# 5. Get all dogs data
@dogs_blueprint.route('/dogs_data/all', methods=['GET'])
def get_all_dogs_data():
    """
    Retrieve a list of all dog breeds
    ---
    responses:
        200:
            description: Dogs' breeds retrieved successfully
        500:
            description: An error occurred while deleting the dog data
    """
    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        all_dogs=[]
        for breed in db.list_collection_names():
            breed_data = db[breed].find()
            for dog_data in breed_data:
                dog_data['_id'] = str(dog_data['_id'])
                all_dogs.append(dog_data)
        return jsonify(all_dogs),200
    except Exception as e:
        return jsonify({"error": str(e)}),500

# 6. Get all dogs breeds and URL
@dogs_blueprint.route('/dogs_data/BreedsAndUrl', methods=['GET'])
def get_all_dogs_breeds_and_url():
    """
    Retrieve a list of all dog breeds and URL picture
    ---
    responses:
        200:
            description: Dogs' breeds retrieved successfully
        500:
            description: An error occurred while deleting the dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        breed_images = []
        for breed in db.list_collection_names():
            breed_data = db[breed].find_one({},{"_id":0,"pic_url":1})
            if breed_data and "pic_url" in breed_data:
                breed_images.append({"breed_name":breed, "pic_url":breed_data["pic_url"]})
        return jsonify(breed_images),200
    except Exception as e:
        return jsonify({"error": str(e)}),500

################################# UPDATE #################################

# 7. Update dog data by breed and age range
@dogs_blueprint.route('/dogs_data/<breed_name>/<gender>/<from_age>/<to_age>', methods=['PUT'])
def update_dog_data_by_breed_and_age_range(breed_name,gender,from_age,to_age):
    """
    Update dog data by its breed and age range
    ---
    parameters:
        - name: breed_name
          in: path
          required: true
          description: The breed_name of the dog data to retrieve
        - name: gender
          in: path
          required: true
          description: The gender of the dog data to retrieve
        - name: from_age
          in: path
          required: true
          description: The from_age of the dog data to retrieve
        - name: to_age
          in: path
          required: true
          description: The to_age of the dog data to retrieve
        - name: updated_data
          in: body
          required: true
          description: The dog data to create
          schema:
            id: UpdatedData
            optional:
                - avg_height_min
                - avg_height_max
                - avg_weight_min
                - avg_weight_max
                - avg_drink
                - avg_food
                - pic_url
            properties:
                avg_height_min:
                    type: string
                    description: The aevrage height of the dog
                avg_height_max:
                    type: string
                    description: The aevrage height of the dog
                avg_weight_min:
                    type: string
                    description: The average weight of the dog
                avg_weight_max:
                    type: string
                    description: The average weight of the dog
                avg_drink:
                    type: string
                    description: The average drinking recommended for the dog
                avg_food:
                    type: string
                    description: The average eating recommended for the dog
                pic_url:
                    type: string
                    description: URL of picture of the dog breed
    responses:
        200:
            description: Dog data updated successfully
        404:
            description: Dog data not found
        500:
            description: An error occurred while updating the dog data
    """

    data = request.json
    db = MongoConnectionHolder.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    if round(float(data['avg_height_min']),2) > round(float(data['avg_height_max']),2):
        return jsonify({"error":"'avg_height_min' must be smaller than 'avg_height_max'"}),400
    
    if round(float(data['avg_weight_min']),2) > round(float(data['avg_weight_max']),2):
        return jsonify({"error":"'avg_weight_min' must be smaller than 'avg_weight_max'"}),400
    try:
        package_collection = db[breed_name]
        updates = {"updated_at":datetime.now()}
        for field in ['avg_height_min','avg_height_max', 'avg_weight_min','avg_weight_max','avg_drink','avg_food','pic_url']:
            if field in data:
                updates[field] = round(float(data[field]), 2) if field.startswith('avg_') else data[field]
        result = package_collection.update_one(
            {"from_age":float(from_age),"to_age":float(to_age),"gender":gender},
            {"$set":updates}
        )
        if result.matched_count == 0:
            return jsonify({"error":"No data found for this breed and age range"}),404
        updated_dog_data = package_collection.find_one({"from_age": float(from_age) , "to_age":float(to_age)})
        return jsonify(updated_dog_data),200
    except Exception as e:
        return jsonify({"error": str(e)}),500

################################# DELETE #################################

# 8. Delete all dogs data
@dogs_blueprint.route('/dogs_data', methods=['DELETE'])
def delete_all_dogs_data():
    """
    Delete all dog data
    ---
    responses:
        200:
            description: All dogs data deleted successfully
        500:
            description: An error occurred while deleting all dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        for collection_name in db.list_collection_names():
            db[collection_name].drop()
        return jsonify({"message": "All dog data deleted successfully"}),200
    except Exception as e:
        return jsonify({"error": str(e)}),500

# 9. Delete dog data by breed and age range
@dogs_blueprint.route('/dogs_data/<breed>/<gender>/<from_age>/<to_age>', methods=['DELETE'])
def delete_dog_data_by_breed_and_age(breed,gender,from_age,to_age):
    """
    Delete dog data by breed and age range
    ---
    parameters:
        - name: breed
          in: path
          required: true
          description: The breed name of the dog data to delete
        - name: gender
          in: path
          required: true
          description: The breed name of the dog data to delete
        - name: from_age
          in: path
          required: true
          description: The starting age of the dog data
        - name: to_age
          in: path
          required: true
          description: The ending age of the dog data
    responses:
        200:
            description: Dog data deleted successfully
        404:
            description: No data found for the specified breed and age range
        500:
            description: An error occurred while deleting all dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        package_collection = db[breed]
        result = package_collection.delete_one({"gender" : gender, "from_age": float(from_age), "to_age":float(to_age)})
        if result.deleted_count > 0:
            return jsonify({"message": "Dog data deleted successfully"}),200
        else:
            return jsonify({"error": "Dog data not found for this breed and age range"}),404

    except Exception as e:
        return jsonify({"error": str(e)}),500

# 10. Delete dog data by UUID
@dogs_blueprint.route('/dogs_data/<dog_uuid>', methods=['DELETE'])
def delete_dog_data_by_uuid(dog_uuid):
    """
    Delete dog data by UUID
    ---
    parameters:
        - name: dog_uuid
          in: path
          required: true
          description: The dog_uuid of the dog data to delete
    responses:
        200:
            description: All dogs data deleted successfully
        500:
            description: An error occurred while deleting all dog data
    """

    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    try:
        for breed in db.list_collection_names():
            result = db[breed].delete_one({"_id":dog_uuid})
            if result.deleted_count > 0:
                return jsonify({"message": "Dog data deleted successfully"}),200
        return jsonify({"message": "Dog data not found"}),404
    except Exception as e:
        return jsonify({"error": str(e)}),500