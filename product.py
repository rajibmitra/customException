ot():
    """ Patterns to get the output """
    help_text = {
        'http://127.0.0.1:5000/': 'shows homepage or helps page',
        'http://127.0.0.1:5000/products': 'shows all the TD product names',
        'http://127.0.0.1:5000/products/teradata_viewpoint': 'shows general product info for\
         product Teradata Viewpoint',
        'http://127.0.0.1:5000/products/teradata_viewpoint/15.10': 'properties for Teradata Viewpoint 15.00'
    }
    return jsonify({'message': 'HomePage, directs you what to do next'}, help_text)


@app.route('/version')
def get_package_version():
    return jsonify(version=__version__)


@app.route('/products')
def get_products():
    return jsonify(products=get_product_list())


@app.route('/products/<product_id>')
@product_validator
def get_versions(product_id):
    version_dict_list = get_product_versions(product_id)
    return jsonify(product_id=product_id,
                   product_version_ranges=version_dict_list)


@app.route('/products/<product_id>/<product_version>')
@product_validator
def get_version_compatible_products(product_id, product_version):
    compatible_product_ids = get_compatible_product_ids(product_id, product_version)
    compatible_products = [{'product_id': item} for item in compatible_product_ids]
    return jsonify({'product_id': product_id,
                    'compatible_products': compatible_products})


@app.route('/products/<product_id>/<product_version>/compatible-products/<compatible_product_id>')
@product_validator
def get_version_specifics(product_id, product_version, compatible_product_id):
    compatibility_list = get_product_compatible_versions(product_id, product_version, compatible_product_id)
    return jsonify(product_id=product_id,
                   compatibility=compatibility_list)


@app.route('/ecosystem-upgrade', methods=['POST', 'GET'])
def ecosystem_upgrade():
    if request.method == 'GET':
        return jsonify({"message": "Get method is not allowed for this api"}), 405
    data_dict = request.get_json()  # validating payload here

    payload_checker = ValidateEcosystemPayload(data_dict)
    payload_checker.validate_ecosystem_post()

    eco = Ecosystem(Compatibility())
    eco.load_ecosystem(data_dict["current_ecosystem"], data_dict["desired_upgrade"])
    compatibility = eco.check_compatibility()
    return jsonify(compatibility)
