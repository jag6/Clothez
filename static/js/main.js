// CSRF TOKEN
const getToken = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if(cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
let csrftoken = getToken('csrftoken');


// COOKIE
const getCookie = (name) => {
    let cookieArr = document.cookie.split(';');

    for (let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split('=');
        if(name == cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
};

// cart cookie
let cart = JSON.parse(getCookie('cart'));
const updateCart = () => {
    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/;secure;http-only;samesite=lax;';
};
if (cart == undefined) {
    cart = {};
    updateCart();
}

// wishlist cookie
let wishlist = JSON.parse(getCookie('wishlist'));
const updateWishlist = () => {
    document.cookie = 'wishlist=' + JSON.stringify(wishlist) + ';domain=;path=/;secure;http-only;samesite=lax';
};
if (wishlist == undefined) {
    wishlist = {};
    updateWishlist();   
}

// purposely made global for use in multiple functions
const cartItems = document.getElementById('cart-items');

const getCartItemsAndTotal = () => {
    let cart_total;
	let order = {'cart_total': 0, 'cart_items': 0};
    let items = [];

    for(let i in cart) {
        if(cart[i]['quantity'] > 0) {
            cart_total = (cart[i]['price'] * cart[i]['quantity']);
            order['cart_total'] += cart_total;
            order['cart_items'] += cart[i]['quantity'];

            let item = {
                'id': cart[i]['id'],
                'quantity': cart[i]['quantity']
            }
            items.push(item);

            let itemQuantity = document.querySelectorAll('.item-quantity');
            if(itemQuantity) {
                itemQuantity.forEach((item) => {
                    item.innerHTML = `
                        ${items.map((item) => `
                            <div class="iq-child" data-product=${item.id}>${item.quantity}</div>
                        `).join('\n')}
                    `;
                    const iqChildren = document.querySelectorAll('.iq-child');
                    iqChildren.forEach((child) => {
                        if(child.dataset.product !== child.parentNode.dataset.product) {
                            child.remove();
                        }
                    });
                });
            }
        }
    }

    // show total $ of cart items
    const cartTotal = document.getElementById('cart-total');
    if(cartTotal) {
        cartTotal.innerText = 'Total: $' + order['cart_total'].toFixed(2);
    }

    // show # of cart items
    if(order['cart_items'] === 0) {
        cartItems.innerText = '';
    }else {
        cartItems.innerText = order['cart_items'];
    }
};

// cart items animation
const cartItemsAnimationAdd =  [
    { transform: 'rotate(0px)' },
    { transform: 'rotate(15deg)' },
    { transition: 'ease-in-out' }
];
const cartItemsAnimationRemove =  [
    { transform: 'rotate(0px)' },
    { transform: 'rotate(-15deg)' },
    { transition: 'ease-in-out' }
];
const cartItemsAnimationTiming = {
    duration: 1000,
    iterations: 1,
};

// wishlist animation
const wishlistAnimationTransform = [
    { transform: 'scale(1)' },
    { transform: 'scale(1.2)'},
    { transition: 'ease-in-out' }
];
const wishlistIconAnimationTiming = {
    duration: 1000,
    iterations: 1,
};

// update cart and wishlist
const addToCart = (product_id, price) => {
    if(cart[product_id] == undefined) {
        cart[product_id] = {'id': product_id, 'quantity': 1, 'price': price}; 
    }else {
        cart[product_id]['quantity'] += 1;
    }
    updateCart();
    getCartItemsAndTotal();
    cartItems.animate(cartItemsAnimationAdd, cartItemsAnimationTiming);
};

if(document.querySelector('.update-btn')) {
    const updateBtns = document.querySelectorAll('.update-btn');
    updateBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const product_id = btn.dataset.product;
            const price = btn.dataset.price;
            const action = btn.dataset.action;

            switch(action) {
                case 'add-to-cart':
                    addToCart(product_id, price);
                    break;
                case 'remove-from-cart':
                    cart[product_id]['quantity'] -= 1;
                    updateCart();
                    getCartItemsAndTotal();
                    cartItems.animate(cartItemsAnimationRemove, cartItemsAnimationTiming);
                    // fully remove from cart cookie
                    if(cart[product_id]['quantity'] <= 0) {
                        delete cart[product_id];
                        updateCart();
                        window.location.reload();
                    }
                    break;
                case 'add-to-wishlist':
                    if(wishlist[product_id] == undefined) {
                        wishlist[product_id] = {'quantity': 1, 'price': price};
                    }
                    document.getElementById('wishlist-icon').animate(wishlistAnimationTransform, wishlistIconAnimationTiming);
                    updateWishlist();
                    break;
                case 'add-to-cart-from-wishlist':
                    addToCart(product_id, price);
                    delete wishlist[product_id];
                    updateWishlist();
                    window.location.reload();
                    break;
                case 'remove-from-wishlist':
                    delete wishlist[product_id];
                    updateWishlist();
                    window.location.reload();
                    break;
            }
        });
    });
}

// show # of cart items in header on all pages
window.addEventListener('load', () => {
    getCartItemsAndTotal();
});


// ALERT MESSAGES
if(document.querySelector('.alert-message')) {
    const alertMessages = document.querySelectorAll('.alert-message');
    alertMessages.forEach((message) => {
        message.classList.add('fade-out');
        setTimeout(() => {
            message.remove();
        }, 5000);
    });
}


// ANIMATIONS
const scrollElements = document.querySelectorAll('.js-scroll');
var throttleTimer;
const throttle = (callback, time) => {
    if(throttleTimer) return;
    throttleTimer = true;
    setTimeout(() => {
        callback();
        throttleTimer = false;
    }, time);
};
const elementInView = (el, dividend = 1) => {
    const elementTop = el.getBoundingClientRect().top;
  	return (
    	elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend
	);
};
const elementOutofView = (el) => {
  	const elementTop = el.getBoundingClientRect().top;
  	return (
    	elementTop > (window.innerHeight || document.documentElement.clientHeight)
  	);
};
const displayScrollElement = (element) => {
  	element.classList.add('scrolled');
};
const hideScrollElement = (element) => {
 	element.classList.remove('scrolled');
};
const handleScrollAnimation = () => {
	scrollElements.forEach((el) => {
    	if(elementInView(el, 1.25)) {
      	    displayScrollElement(el);
    	} else if(elementOutofView(el)) { 
            hideScrollElement(el)
        }
  	});
};
window.addEventListener('scroll', () => { 
	throttle(() => {
        handleScrollAnimation();
    }, 250);
});


// CHATBOX
if(document.querySelector('#open-popup')) {
    const openPU = document.getElementById('open-popup');
    const chatPU = document.getElementById('chat-popup');
    const closePU = document.getElementById('close-popup');

    openPU.addEventListener('click', () => {
        chatPU.style.display = 'flex';
        openPU.style.display = 'none';
    });
    closePU.addEventListener('click', () => {
        chatPU.style.display = 'none';
        openPU.style.display = 'flex';
    });
}


// BACK BTN
if(document.getElementById('back-btn')) {
    document.getElementById('back-btn').addEventListener('click', () => {
        close();
    });
};