const getToken = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
let csrftoken = getToken('csrftoken');

const getCookie = (name) => {
    // Split cookie string and get all individual name=value pairs in an array
    let cookieArr = document.cookie.split(";");

    for (let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");

        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name == cookiePair[0].trim()) {
            // Decode the cookie value and return
            return decodeURIComponent(cookiePair[1]);
        }
    }

    // Return null if not found
    return null;
}

let cart = JSON.parse(getCookie('cart'));
if (cart == undefined) {
    cart = {};
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/;secure;http-only;samesite=lax;";
}

const addCartItem = (productId, action) => {
    if (action == 'add'){
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': 1}; 
        } else{
            cart[productId]['quantity'] += 1;
        }
    }
    if (action == 'remove'){
        cart[productId]['quantity'] -= 1
        if (cart[productId]['quantity'] <= 0) {
            delete cart[productId];
        }
    }
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/;secure;http-only;samesite=lax;";

    location.reload();
}

const updateCart = async (productId, action) => {
    try {
        const response = await fetch('/update_item/', {
            method:'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            }, 
            body: JSON.stringify({ productId: productId, action: action })
        });
        if(!response.ok) {
            throw new Error(`${response.status}`);
        }
        await response.json();
        location.reload();
    } catch (error) {
        console.log(error);
    }
}

const updateBtns = document.querySelectorAll('.update-cart');
updateBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        let productId = btn.dataset.product;
        let action = btn.dataset.action;
        console.log('ProductId:', productId, 'Action:', action);

        if (user == 'AnonymousUser'){
            addCartItem(productId, action);
        }else{
            updateCart(productId, action);
        }
    });
});