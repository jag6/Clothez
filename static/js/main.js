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
}
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
}

// CART AND WISHLIST
let cart = JSON.parse(getCookie('cart'));
const updateCart = () => {
    const update = document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/;secure;http-only;samesite=lax;';
    return update;
}
if (cart == undefined) {
    cart = {};
    updateCart();
}

const addToCart = (product_id) => {
    if(cart[product_id] == undefined) {
        cart[product_id] = {'quantity': 1}; 
    }else {
        cart[product_id]['quantity'] += 1;
    }
}

let wishlist = JSON.parse(getCookie('wishlist'));
const updateWishlist = () => {
    const update = document.cookie = 'wishlist=' + JSON.stringify(wishlist) + ';domain=;path=/;secure;http-only;samesite=lax';
    return update;
}
if (wishlist == undefined) {
    wishlist = {};
    updateWishlist();   
}

const updateCartAndWishlist = (product_id, action) => {
    switch(action) {
        case 'add-to-cart':
            addToCart(product_id);
            updateCart();
            break;
        case 'remove-from-cart':
            cart[product_id]['quantity'] -= 1
            if(cart[product_id]['quantity'] <= 0) {
                delete cart[product_id];
            }
            updateCart();
            break;
        case 'add-to-wishlist':
            if(wishlist[product_id] == undefined) {
                wishlist[product_id] = {'quantity': 1};
            }
            updateWishlist();
            break;
        case 'add-to-cart-from-wishlist':
            addToCart(product_id);
            updateCart();
            delete wishlist[product_id];
            updateWishlist();
            break;

        case 'remove-from-wishlist':
            delete wishlist[product_id];
            updateWishlist();
            break;
    }
    window.location.reload();
}

if(document.querySelector('.update-btn')) {
    const updateBtns = document.querySelectorAll('.update-btn');
    updateBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            let product_id = btn.dataset.product;
            let action = btn.dataset.action;

            updateCartAndWishlist(product_id, action);
        });
    });
}


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