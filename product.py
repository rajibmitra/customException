""" Flask Rest API Framework around the core DMS,
shows the list of the products and its dependencies based on a query
"""
import logging
import traceback
from functools import wraps
from flask import Flask, jsonify, request
from system_change_dms.db import get_product_list, make_db, get_product_versions, \
    get_product_compatible_versions, get_compatible_product_ids, Compatibility
from system_change_dms.ecosystem import Ecosystem
from system_change_dms.flask_dms.exception import InvalidProductError, PropertyMissingInPost, \
    NoBodyFound, InvalidProductIdException, \
    InvalidComponentId, DuplicateComponentId, ComponentIdNotExist, BadProductVersion,\
    ProductVersionOutOfRange, UpgradeVersionOutOfRange, BadUpgradeVersion, PropertyTypeError
from system_change_dms.flask_dms.validation import ValidateEcosystemPayload
from system_change_dms import __version__


app = Flask(__name__)
try:
    make_db()  # TODO: move this call to a better location
except:
    print('Was unable to generate the sqlite3 database. Must be a production deployment...')
    # tried to make db but was unable- must be production env
    pass


@app.errorhandler(InvalidProductError)
def handle_invalid_usage(error):
    """ register error handler for InvalidProductError class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(InvalidProductIdException)
def handle_invalid_product_id(error):
    """register error handler for Invalid product id"""
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(PropertyMissingInPost)
def handle_missing_property(error):
    """ register error handler for PropertyMissingInPost class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(PropertyTypeError)
def handle_property_type(error):
    """ register error handler for PropertyTypeError class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(BadUpgradeVersion)
def handle_bad_version_string_in_upgrade(error):
    """ register error handler for BadUpgradeVersion class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(UpgradeVersionOutOfRange)
def handle_out_of_range_in_upgrade(error):
    """ register error handler for UpgradeVersionOutOfRange class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(ProductVersionOutOfRange)
def handle_out_of_range_product_version(error):
    """ register error handler for ProductVersionOutOfRange class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(InvalidComponentId)
def handle_component_id(error):
    """ register error handler for InvalidComponentId class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(NoBodyFound)
def no_body_found(error):
    """ register error handler for NoBodyFound class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(BadProductVersion)
def handle_invalid_product_version(error):
    """ register error handler for BadProductVersion class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(DuplicateComponentId)
def handle_duplicate_component_id(error):
    """ register error handler for DuplicateComponentId class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(ComponentIdNotExist)
def handle_component_id_not_exist(error):
    """ register error handler for ComponentIdNotExist class """
    response = jsonify(error.to_dict())
    return response, 400


@app.errorhandler(Exception)
def exception_wrapper(the_exception):
    try:
        log_unexpected_exception(the_exception=the_exception,
                                 the_traceback=traceback,
                                 the_request=request)
    except:
        # broad catching here is OK, as we do not want it going any further
        logging.error("Exception-logging code raised an unexpected exception.")
    return jsonify(message="Internal Server Error"), 500


def log_unexpected_exception(the_exception, the_traceback, the_request):
    """
    This function is intended to log a detailed message about an unexpected
    exception. No global variables or anything special is needed, which allows
    us to unit test this function without added complexity.
    :param the_exception: the exception raised
    :param the_traceback: the traceback top-level object used to generate stack traces
    :param the_request: the Flask request object, 'request' when within a request context
    :return: None
    """
    exception_message = 'Unhandled exception at the flask app level.\n'
    exception_message += 'Outputting stacktrace (not sent to REST clients):\n'
    exception_message += the_traceback.format_exc() + '\n'
    # We must have a Flask 'request context', as jsonify does not work otherwise
    exception_message += 'Request info:\n'
    attributes = ['base_url', 'remote_addr', 'method', 'query_string']
    for attribute in attributes:
        # Get value, and wrap in str() to convert None type to ''
        value_raw = getattr(the_request, attribute, None)
        value = str(value_raw)
        exception_message += '  ' + attribute + ': ' + value + '\n'
    logging.error(exception_message)


def product_validator(view_func):
    """ decorator to validate product_id, product_version and compatible_product_id
    @wraps takes a function to be decorated and adds the functionality of
    copying over the function name, arguments list """

    @wraps(view_func)
    def validation_decorator(product_id, product_version=None, compatible_product_id=None):
        """ validates endpoints and throws error message in case NULL value """
        version_dict_list = get_product_versions(product_id)
        if not version_dict_list:
            error_message = 'Invalid product_id: %s' % product_id
            raise InvalidProductError(error_message)

        if not product_version and not compatible_product_id:
            # return, when product_id endpoint is being called
            return view_func(product_id)

        if product_version:
            compatible_product_ids = get_compatible_product_ids(product_id, product_version)
            if not compatible_product_ids:
                pass
                error_message = 'Invalid product_version: %s' % product_version
                raise InvalidProductError(error_message)

        if compatible_product_id:
            compatibility_list = get_product_compatible_versions(
                product_id, product_version, compatible_product_id)
            if not compatibility_list:
                error_message = 'Invalid compatible_product_id: %s' % compatible_product_id
                raise InvalidProductError(error_message)
            return view_func(product_id, product_version, compatible_product_id)
        # return, when product_id and product_version endpoint being called
        return view_func(product_id, product_version)

    return validation_decorator


@app.route('/')
def get_root():
    """ Patterns to get the output """
    help_text = {
        'http://127.0.0.1:5000/': 'shows homepage or helps page',
        'http://127.0.0.1:5000/products': 'shows all the my product names',
        'http://127.0.0.1:5000/products/my_viewpoint': 'shows general product info for\
         product my Viewpoint',
        'http://127.0.0.1:5000/products/my_viewpoint/15.10': 'properties for my Viewpoint 15.00'
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
