// MOBILE NAV TOGGLE
const mobile_nav = document.getElementById('mobile-nav');
const nav_overlay = document.getElementById('nav-overlay');
const body = document.querySelector('body');

if(document.getElementById('hamburger-icon')) {
    const clickOff = () => {
        nav_overlay.style.display = 'none';
        mobile_nav.style.width = '0%';
        body.style.overflow = 'auto';
    };
    document.getElementById('hamburger-icon').addEventListener('click', () => {
        if(mobile_nav.style.width === '300px') {
            clickOff();
        }else {
            mobile_nav.style.width = '300px';
            nav_overlay.style.display = 'flex';
            body.style.overflow = 'hidden';
        }
    });
    nav_overlay.addEventListener('click', (e) => {
        if(e.target == nav_overlay) {
            clickOff();
        }
    });
}


// CART
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

let cart = JSON.parse(getCookie('cart'));
if (cart == undefined) {
    cart = {};
    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/;secure;http-only;samesite=lax;';
}

const updateCookieCart = (productId, action) => {
    if(action == 'add') {
        if(cart[productId] == undefined) {
            cart[productId] = {'quantity': 1}; 
        }else {
            cart[productId]['quantity'] += 1;
        }
    }
    if(action == 'remove') {
        cart[productId]['quantity'] -= 1
        if(cart[productId]['quantity'] <= 0) {
            delete cart[productId];
        }
    }
    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/;secure;http-only;samesite=lax;';
    window.location.reload();
}

const updateCart = async (productId, action) => {
    try {
        const response = await fetch('/update_item', {
            method: 'POST',
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
        window.location.reload();
    } catch (error) {
        console.log(error);
    }
}

if(document.querySelector('.update-cart')) {
    const updateBtns = document.querySelectorAll('.update-cart');
    updateBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            let productId = btn.dataset.product;
            let action = btn.dataset.action;

            if(user == 'AnonymousUser') {
                updateCookieCart(productId, action);
            }else {
                updateCart(productId, action);
            }
        });
    });
}


// ANIMATIONS
const scrollElements = document.querySelectorAll('.js-scroll');
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
    	if (elementInView(el, 1.25)) {
      	    displayScrollElement(el);
    	} else if (elementOutofView(el)) { 
            hideScrollElement(el)
        }
  	});
};
window.addEventListener('scroll', () => { 
	handleScrollAnimation();
});