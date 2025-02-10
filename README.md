> [!WARNING]
> This library is still in active development and is not yet ready for production use. The number of supported authentication, pagination, and interaction methods is limited and likely does not cover all use cases. The library is subject to change and may not be stable.
>
> I am very open to feedback and considering others use cases, so please open an issue if you have any suggestions, requests, or issues!

ClientForge is a Python library designed to simplify interactions with REST APIs from Python. It supports a variety of authentication and pagination methods, and provides a robust framework for building and managing Python REST API clients.

It also allows quick and easy handling of results, permitting a variety of filtering and sorting options.

- [Installation](#installation)
- [Overview](#overview)
  - [Components](#components)
- [Creation](#creation)
  - [Model Definitions](#model-definitions)
  - [Client Definition](#client-definition)
- [Simple Usage](#simple-usage)
- [Advanced Usage](#advanced-usage)
  - [Selecting Data](#selecting-data)
  - [Querying Data](#querying-data)
  - [Filtering Data](#filtering-data)
- [Changelog](#changelog)
- [License](#license)
- [Contact](#contact)

## Installation

To install ClientForge, use pip:

```sh
pip install clientforge
```

## Overview

ClientForge is designed to make it easy to create Python interfaces for REST APIs. It provides a simple and consistent interface for making requests, handling authentication, and paginating results. The library is built on top of the `httpx` HTTP library, and provides both synchronous and asynchronous clients.

### Components

A ClientForge client consists of the following components:

- **Client**: The main client object that is used to make requests to the server (sync or async).
- **Auth**: An authentication object that handles the authentication process for the client (ex: OAuth2, API key).
- **Paginator**: A paginator object that handles pagination of results from the server (ex: offset/page pagination).
- **Model**: A series of user-defined model classes that represent the data returned by the REST API.
- **Result**: A generic result class that encapsulates the response data and metadata.
- **Method Definitions**: User-defined methods that make define how the client interacts with the API endpoint.

## Creation

> [!NOTE]
> This section provides an overview of how to create a ClientForge client with examples from the Kroger API. This project is in no way associated with Kroger, and the examples are for illustrative purposes only.
>
> Similarly, the examples are not complete to keep the code concise.

### Model Definitions

The core of response/model mapping is handled by the fantastic [dataclass wizard](https://github.com/rnag/dataclass-wizard) by Ritvik Nag. Almost all of the features of dataclass wizard are supported, including nested dataclasses, aliases, loading and dumping, etc.. Please refer to the dataclass wizard documentation for more information on complex model definitions.

In order to define a model, you need to create a class that inherits from `ForgeModel`.

`models.py`:
```python
from clientforge import ForgeModel
class AisleLocation(ForgeModel):
    bay_number: int
    description: str

class Product(ForgeModel):
    product_id: str
    aisle_locations: list[AisleLocation]
    brand: str
    categories: list[str]
    description: str
```

### Client Definition

With a simple model created, you need to define a client. There are two types of clients: synchronous and asynchronous. Generally, the synchronous client is going to be enough for most use cases so we will focus on that, but the process is nearly identical for the asynchronous client, with the exception of using `AsyncForgeClient` instead of `ForgeClient` and all methods being `async`.

In order to define a client, you need to create a class that inherits from `ForgeClient` and implement the necessary methods:

`client.py`:
```python
from clientforge import (
    AsyncForgeClient,
    ClientCredentialsOAuth2Auth,
    OffsetPaginator,
    Result,
)

from models import Product


class KrogerClient(AsyncForgeClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: list | None = None,
        limit: int = 10,
    ):
        # The details of how to interact with the REST API are provided to the
        #  init method of the ForgeClient class
        super().__init__(
            "https://api.kroger.com/v1/{endpoint}", # Define the base URL for the Kroger API
            auth=ClientCredentialsOAuth2Auth(  # Authenticate with the Kroger API using OAuth2
                "https://api.kroger.com/v1/connect/oauth2/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
            ),
            paginator=OffsetPaginator(  # Use offset pagination to handle large result sets
                page_size=10,
                page_size_param="filter.limit",
                path_to_data="data",
                page_offset_param="filter.start",
                path_to_total="meta.pagination.total",
            ),
        )

        if limit <= 0 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")

    def search_products(
        self,
        terms: list[str] | None = None,
        brand: str | None = None,
        fulfillment: str | None = None,
        location_id: str | None = None,
        product_id: str | None = None,
        top_n: int = 10,
    ) -> Result[Product]:
        # A method definition will accept Python-friendly parameters, and return a Result object
        #  that contains the Model that the user has defined
        if terms and len(terms) > 8:
            raise ValueError("Number of search terms must be less than or equal to 8")

        params = {
            "filter.term": " ".join(terms) if terms else None,
            "filter.brand": brand,
            "filter.fulfillment": fulfillment,
            "filter.locationId": location_id,
            "filter.productId": product_id,
        }
        # The _model_request method is a helper method that handles the request and response
        #  to the REST API, and returns a Result
        # Read the docstring for more information on the parameters
        return self._model_request(
            "GET",
            "products", # The endpoint to interact with
            Product, # The model to coerce the response into
            model_key="data",
            params=params,
            top_n=top_n,
        )

    def get_product(self, product_id: str) -> Result[Product]:
        # It also works for endpoints that return a single object
        return self._model_request(
            "GET",
            f"products/{product_id}",
            Product,
            model_key="data",
        )
```

## Simple Usage

```python
from client import KrogerClient

client = KrogerClient(
    client_id="<YOUR_CLIENT_ID>",
    client_secret="<YOUR_CLIENT_SECRET>",
    scopes=["product.compact"],
)

result = client.search_products(terms=["milk"], top_n=5)
print(result)
# Result([Product(<data>), Product(<data>), ...])

result = client.get_product("0001111000000")
print(result[0])
# Product(<data>)
```

## Advanced Usage

> [!WARNING]
> The following features are still in development and may not work as expected. They are subject to change. They are designed to provide a more robust and flexible interface for interacting with the results, but may return inconsistent results or errors.

### Selecting Data

Data can be selected and returned into a dictionary or list of dictionaries using the `select` method. The `select` method accepts a list of keys to select from the data, and returns a list of dictionaries with the selected keys. Each key can be a simple key, or a JSONPath expression.

```python
result = client.search_products(terms=["milk"], top_n=5)

print(result.select("product_id", "brand"))
# [{'product_id': '0001111000000', 'brand': 'Kroger'}, ...]

print(result.select("product_id, brand"))
# [{'product_id, brand': ['0001111000000', 'Kroger'], ...]

print(result.select("product_id", item_price="items[*].price.regular"))
# [{'product_id': '0001111000000', 'item_price': [1.99, 2.99, ...], ...]
```

### Querying Data

Data can be filtered using JSONPath syntax using the `query` method. The `query` method accepts a JSONPath expression and returns a Result object containing the filtered data. Note that this does not return a list of the original data, but a Result object containing the filtered data.

```python
print(result.query("items[?(price.regular > 2.00)]")) # Get all items with a regular price greater than $2.00
# Result([Item(<data>), Item(<data>), ...]) (note that the result is not Product objects, but Item objects)

print(products.query("items[*].price.regular"))
# Result(1.99, 2.99, ...)

print(products.query("items[*].price.regular + 10"))
# Result(11.99, 12.99, ...)
```

### Filtering Data

Data can be filtered using the `filter` method. The `filter` method accepts a series of properties and conditionals from the defined model, and returns a Result object containing the filtered data.

> [!NOTE]
> This feature is still in heavy development and may not work as expected. It is styled after the SQLAlchemy ORM, and is intended to provide a similar experience.

```python
print(products.filter(Product.product_id == "0003400029105"))
# Result([Product(<data>)])

print(products.filter(Product.brand == "Kroger"))
# Result([Product(<data>), Product(<data>), ...])

print(products.filter(Product.items.where.any(Item.price.regular > 0)))
# Result([Product(<data>), Product(<data>), ...])

print(products.filter(Product.items.length == 1))
# Result([Product(<data>), Product(<data>), ...])
```


## Changelog

See the CHANGELOG.md for details on changes and updates.

## License

This project is licensed under the terms of the license found in the LICENSE file.

## Contact

For any inquiries or issues, please open an issue on GitHub.
