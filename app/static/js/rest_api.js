$(function () {

    // Auth token storage - try to load from localStorage first
    let authToken = localStorage.getItem('authToken') || null;
    
    // Category mapping (from database)
    const CATEGORY_MAP = {
        'CLOTHS': 1,
        'FOOD': 2,
        'HOUSEWARES': 3,
        'AUTOMOTIVE': 4,
        'TOOLS': 5,
        'UNKNOWN': 6
    };

    // Helper function to always get the latest token
    function getAuthToken() {
        if (!authToken) {
            authToken = localStorage.getItem('authToken');
        }
        return authToken;
    }

    // Helper function to save token
    function setAuthToken(token) {
        authToken = token;
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    }

    // ****************************************
    // LOGIN FUNCTION
    // ****************************************

    $("#login-btn").click(function() {
        let email = $("#login_email").val();
        let password = $("#login_password").val();
        
        $.ajax({
            type: "POST",
            url: "/api/v1/auth/login",
            contentType: "application/json",
            data: JSON.stringify({email: email, password: password}),
            success: function(res) {
                setAuthToken(res.access_token);
                flash_message("Login successful!");
                $("#login-section").hide();
            },
            error: function(res) {
                flash_message("Login failed: " + (res.responseJSON?.error || "Unknown error"));
            }
        });
    });

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_description").val(res.description);
        if (res.available == true) {
            $("#product_available").val("true");
        } else {
            $("#product_available").val("false");
        }
        // Convert category_id back to category name for display
        const categoryName = Object.keys(CATEGORY_MAP).find(
            key => CATEGORY_MAP[key] === res.category_id
        ) || "UNKNOWN";
        $("#product_category").val(categoryName);
        $("#product_price").val(res.price);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_name").val("");
        $("#product_description").val("");
        $("#product_available").val("");
        $("#product_category").val("");
        $("#product_price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product (requires auth)
    // ****************************************

    $("#create-btn").click(function () {
        // Ensure we have the latest token
        let token = getAuthToken();
        
        // Check if logged in
        if (!token) {
            flash_message("Please login first!");
            return;
        }

        let name = $("#product_name").val();
        let description = $("#product_description").val();
        let available = $("#product_available").val() == "true";
        let category = $("#product_category").val();
        let price = parseFloat($("#product_price").val());

        // Validate required fields
        if (!name) {
            flash_message("Product name is required");
            return;
        }
        if (!price || isNaN(price)) {
            flash_message("Valid price is required");
            return;
        }
        if (!category || !CATEGORY_MAP[category]) {
            flash_message("Valid category is required");
            return;
        }

        let data = {
            "name": name,
            "description": description,
            "available": available,
            "category_id": CATEGORY_MAP[category],
            "price": price
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/v1/products",
            contentType: "application/json",
            headers: {"Authorization": "Bearer " + token},
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Product created successfully!");
        });

        ajax.fail(function(res){
            if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message);
            } else if (res.status === 401) {
                flash_message("Unauthorized. Please login again.");
                setAuthToken(null);  // Clear invalid token
            } else if (res.status === 400) {
                flash_message("Bad request. Please check all fields.");
            } else {
                flash_message("Error creating product");
            }
        });
    });

    // ****************************************
    // Update a Product (requires auth)
    // ****************************************

    $("#update-btn").click(function () {
        // Ensure we have the latest token
        let token = getAuthToken();
        
        // Check if logged in
        if (!token) {
            flash_message("Please login first!");
            return;
        }

        let product_id = $("#product_id").val();
        
        // Check if product_id exists
        if (!product_id) {
            flash_message("Please retrieve a product first");
            return;
        }

        let name = $("#product_name").val();
        let description = $("#product_description").val();
        let available = $("#product_available").val() == "true";
        let category = $("#product_category").val();
        let price = parseFloat($("#product_price").val());

        let data = {
            "name": name,
            "description": description,
            "available": available,
            "category_id": CATEGORY_MAP[category],
            "price": price
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/v1/products/${product_id}`,
            contentType: "application/json",
            headers: {"Authorization": "Bearer " + token},
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Product updated successfully!");
        });

        ajax.fail(function(res){
            if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message);
            } else if (res.status === 401) {
                flash_message("Unauthorized. Please login again.");
                setAuthToken(null);  // Clear invalid token
            } else if (res.status === 404) {
                flash_message("Product not found");
            } else {
                flash_message("Error updating product");
            }
        });
    });

    // ****************************************
    // Delete a Product (requires auth)
    // ****************************************

    $("#delete-btn").click(function () {
        // Ensure we have the latest token
        let token = getAuthToken();
        
        // Check if logged in
        if (!token) {
            flash_message("Please login first!");
            return;
        }

        let product_id = $("#product_id").val();
        
        // Check if product_id exists
        if (!product_id) {
            flash_message("Please retrieve a product first");
            return;
        }

        if (!confirm("Are you sure you want to delete this product?")) {
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/v1/products/${product_id}`,
            contentType: "application/json",
            headers: {"Authorization": "Bearer " + token},
            data: '',
        });

        ajax.done(function(res){
            clear_form_data();
            $("#product_id").val("");
            flash_message("Product has been deleted!");
        });

        ajax.fail(function(res){
            if (res.status === 401) {
                flash_message("Unauthorized. Please login again.");
                setAuthToken(null);  // Clear invalid token
            } else if (res.status === 404) {
                flash_message("Product not found");
            } else {
                flash_message("Server error!");
            }
        });
    });

    // ****************************************
    // Retrieve a Product (no auth required)
    // ****************************************

    $("#retrieve-btn").click(function () {

        let product_id = $("#product_id").val();
        
        if (!product_id) {
            flash_message("Please enter a product ID");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/v1/products/${product_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Product retrieved successfully!");
        });

        ajax.fail(function(res){
            clear_form_data();
            if (res.status === 404) {
                flash_message("Product not found");
            } else {
                flash_message(res.responseJSON?.message || "Error retrieving product");
            }
        });
    });

    // ****************************************
    // Clear the form (no auth required)
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });

    // ****************************************
    // Search for Products (no auth required)
    // ****************************************

		$("#search-btn").click(function () {
				let name = $("#product_name").val();
				let description = $("#product_description").val();
				let available = $("#product_available").val() == "true";
				let category = $("#product_category").val();

				let queryString = "";
				if (name) queryString += 'name=' + encodeURIComponent(name);
				if (description) {
						if (queryString.length > 0) queryString += '&';
						queryString += 'description=' + encodeURIComponent(description);
				}
				if (available) {
						if (queryString.length > 0) queryString += '&';
						queryString += 'available=' + available;
				}
				if (category && category !== 'UNKNOWN') {
						if (queryString.length > 0) queryString += '&';
						queryString += 'category_id=' + CATEGORY_MAP[category];
				}

				$("#flash_message").empty();

				$.ajax({
						type: "GET",
						url: `/api/v1/products${queryString ? '?' + queryString : ''}`,
						contentType: "application/json",
						success: function(res) {
								// Clear and build table
								var container = document.getElementById("search_results");
								container.innerHTML = '';
								
								if (!res || res.length === 0) {
										container.innerHTML = '<p>No products found</p>';
										flash_message("No products found");
										return;
								}
								
								// Build table using DOM methods
								var table = document.createElement('table');
								table.className = 'table table-striped';
								table.setAttribute('cellpadding', '10');
								
								// Header
								var thead = document.createElement('thead');
								var headerRow = document.createElement('tr');
								var headers = ['ID', 'Name', 'Description', 'Available', 'Category', 'Price'];
								for (var h = 0; h < headers.length; h++) {
										var th = document.createElement('th');
										th.textContent = headers[h];
										headerRow.appendChild(th);
								}
								thead.appendChild(headerRow);
								table.appendChild(thead);
								
								// Body
								var tbody = document.createElement('tbody');
								var firstProduct = null;
								
								for (var i = 0; i < res.length; i++) {
										var product = res[i];
										var categoryName = Object.keys(CATEGORY_MAP).find(
												key => CATEGORY_MAP[key] === product.category_id
										) || "UNKNOWN";
										
										var row = document.createElement('tr');
										
										var cellId = document.createElement('td');
										cellId.textContent = product.id;
										row.appendChild(cellId);
										
										var cellName = document.createElement('td');
										cellName.textContent = product.name;
										row.appendChild(cellName);
										
										var cellDesc = document.createElement('td');
										cellDesc.textContent = product.description;
										row.appendChild(cellDesc);
										
										var cellAvail = document.createElement('td');
										cellAvail.textContent = product.available;
										row.appendChild(cellAvail);
										
										var cellCat = document.createElement('td');
										cellCat.textContent = categoryName;
										row.appendChild(cellCat);
										
										var cellPrice = document.createElement('td');
										cellPrice.textContent = product.price;
										row.appendChild(cellPrice);
										
										tbody.appendChild(row);
										
										if (i === 0) firstProduct = product;
								}
								
								table.appendChild(tbody);
								container.appendChild(table);
								
								if (firstProduct) update_form_data(firstProduct);
								flash_message("Found " + res.length + " product(s)");
						},
						error: function(res) {
								flash_message(res.responseJSON?.message || "Error searching products");
						}
				});
		});

});
