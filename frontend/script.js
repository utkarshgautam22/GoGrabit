// GoGrabit - Customer Frontend Script

let products = [];
let cart = [];
let favorites = JSON.parse(localStorage.getItem('gg_favorites') || '[]');
let activeReservation = null;
let userProfile = JSON.parse(localStorage.getItem('gg_user_profile') || 'null');
let darkMode = localStorage.getItem('gg_dark_mode') === '1';
let offerIndex = 0;
let offerInterval = null;
let reserveInterval = null;

if (darkMode) document.body.classList.add('dark');

const OFFERS = [
    { title: 'Quick Delivery', desc: 'Order & collect in 15 mins', color: '#ff8a6b' },
    { title: 'Fresh Stock', desc: 'Daily restocked items', color: '#f5b56a' },
    { title: 'Budget Friendly', desc: 'Affordable quality products', color: '#7cc6ff' }
];

// DOM Elements
const productsEl = document.getElementById('products');
const categoriesEl = document.getElementById('categories');
const searchInput = document.getElementById('searchInput');
const offerTrack = document.getElementById('offerTrack');
const popQty = document.getElementById('popQty');
const popTotal = document.getElementById('popTotal');
const openCartBtn = document.getElementById('openCart');
const cartPage = document.getElementById('cartPage');
const cartItemsEl = document.getElementById('cartItems');
const cartTotalEl = document.getElementById('cartTotal');
const topCartCount = document.getElementById('topCartCount');
const topCartBtn = document.getElementById('topCartBtn');
const reserveBtn = document.getElementById('confirmReserve');
const custName = document.getElementById('custName');
const custPhone = document.getElementById('custPhone');
const custRoom = document.getElementById('custRoom');
const reservationInfo = document.getElementById('reservationInfo');
const searchClear = document.getElementById('clearSearch');
const closeCartBtn = document.getElementById('closeCart');
const themeToggle = document.getElementById('themeToggle');

// Toggle Theme
function toggleTheme() {
    darkMode = !darkMode;
    document.body.classList.toggle('dark', darkMode);
    localStorage.setItem('gg_dark_mode', darkMode ? '1' : '0');
    document.getElementById('themeToggle').textContent = darkMode ? '☀️' : '🌙';
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 2200);
}

// Load Products from Backend
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Failed to load products');
        const fetchedProducts = await response.json();
        products = fetchedProducts.filter(p => p.active !== false);
        saveState();
        return products;
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('Failed to load products', 'error');
        loadState();
        return products;
    }
}

// Save/Load State
function saveState() {
    try {
        localStorage.setItem('gg_products', JSON.stringify(products));
        localStorage.setItem('gg_cart', JSON.stringify(cart));
        localStorage.setItem('gg_reservation', JSON.stringify(activeReservation));
    } catch (e) { console.warn('saveState error', e); }
}

function loadState() {
    try {
        const p = localStorage.getItem('gg_products');
        const c = localStorage.getItem('gg_cart');
        const r = localStorage.getItem('gg_reservation');
        if (p) products = JSON.parse(p);
        if (c) cart = JSON.parse(c);
        if (r) {
            activeReservation = JSON.parse(r);
            if (activeReservation && activeReservation.until < Date.now()) {
                activeReservation = null;
                localStorage.removeItem('gg_reservation');
            }
        }
    } catch (e) { console.warn('loadState error', e); }
}

// Load Active Order from Backend
async function loadActiveOrder() {
    try {
        const savedReservation = localStorage.getItem('gg_reservation');
        if (!savedReservation) return;

        const localRes = JSON.parse(savedReservation);
        if (localRes.until < Date.now()) {
            activeReservation = null;
            localStorage.removeItem('gg_reservation');
            return;
        }

        const response = await fetch(`/api/orders/${localRes.id}`);
        if (response.ok) {
            const order = await response.json();
            if (order.status === 'reserved' && new Date(order.expiresAt) > new Date()) {
                activeReservation = localRes;
                showReservation();
                showReservationBanner();
                startReservationTimer();
            } else {
                activeReservation = null;
                localStorage.removeItem('gg_reservation');
            }
        } else {
            activeReservation = null;
            localStorage.removeItem('gg_reservation');
        }
    } catch (error) {
        console.error('Error loading active order:', error);
    }
}

// Save Profile (auto-saved from cart form)
function saveProfile() {
    // This is now called automatically when creating order
    // No separate profile page needed
}

// Render Recent Orders
async function renderRecentOrders() {
    if (!userProfile || !userProfile.phone) {
        const sales = JSON.parse(localStorage.getItem('gg_sales') || '[]').slice(-5).reverse();
        const userBox = document.getElementById('userRecentOrders');
        if (userBox) {
            userBox.innerHTML = sales.length
                ? sales.map(s => `<div>₹${s.total} • ${new Date(s.time).toLocaleTimeString()}</div>`).join('')
                : 'No previous orders';
        }
        return;
    }

    try {
        const response = await fetch('/api/orders');
        if (!response.ok) throw new Error('Failed to fetch orders');

        const allOrders = await response.json();
        const userOrders = allOrders.filter(order => order.phoneNumber === userProfile.phone).slice(0, 5);

        const userBox = document.getElementById('userRecentOrders');
        if (userBox) {
            userBox.innerHTML = userOrders.length
                ? userOrders.map(order => {
                    const status = order.status === 'completed' ? '✅' :
                        order.status === 'cancelled' ? '❌' :
                            order.status === 'picked' ? '📦' : '⏳';
                    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #eee">
                        <div>
                            <div style="font-weight:bold">${status} ${order.orderId}</div>
                            <div style="font-size:12px;color:#666">${new Date(order.createdAt).toLocaleString()}</div>
                        </div>
                        <div style="font-weight:bold;color:#667eea">₹${order.totalAmount}</div>
                    </div>`;
                }).join('')
                : '<div style="color:#999;text-align:center;padding:20px">No previous orders</div>';
        }
    } catch (error) {
        console.error('Error fetching orders:', error);
        const sales = JSON.parse(localStorage.getItem('gg_sales') || '[]').slice(-5).reverse();
        const userBox = document.getElementById('userRecentOrders');
        if (userBox) {
            userBox.innerHTML = sales.length
                ? sales.map(s => `<div>₹${s.total} • ${new Date(s.time).toLocaleTimeString()}</div>`).join('')
                : 'No previous orders';
        }
    }
}

// Render Offers
function renderOffers() {
    offerTrack.innerHTML = '';

    if (!OFFERS || OFFERS.length === 0) {
        const div = document.createElement('div');
        div.className = 'offer';
        div.style.background = 'linear-gradient(90deg, #6b7280, #9ca3af)';
        div.innerHTML = `<h3>No Offers Available</h3><p>Check back later for exciting deals!</p>`;
        offerTrack.appendChild(div);
        return;
    }

    OFFERS.forEach((o, i) => {
        const div = document.createElement('div');
        div.className = 'offer';
        div.style.background = `linear-gradient(90deg, ${o.color}, ${o.color}CC)`;
        div.innerHTML = `<h3>${o.title}</h3><p>${o.desc}</p>`;
        offerTrack.appendChild(div);
    });
}

function startOfferCarousel() {
    if (offerInterval) clearInterval(offerInterval);

    if (!OFFERS || OFFERS.length === 0) {
        offerTrack.style.transform = 'translateX(0%)';
        return;
    }

    if (OFFERS.length === 1) {
        offerTrack.style.transform = 'translateX(0%)';
        return;
    }

    offerIndex = 0;
    function show(i) {
        offerTrack.style.transform = `translateX(-${i * 100}%)`;
    }
    show(0);
    offerInterval = setInterval(() => {
        offerIndex = (offerIndex + 1) % OFFERS.length;
        show(offerIndex);
    }, 3000);
}

// Render Categories
function renderCategories() {
    const cats = Array.from(new Set(products.map(p => p.category)));
    categoriesEl.innerHTML = '';

    const allBtn = document.createElement('div');
    allBtn.className = 'cat active';
    allBtn.textContent = 'All';
    categoriesEl.appendChild(allBtn);
    allBtn.addEventListener('click', () => {
        document.querySelectorAll('.cat').forEach(c => c.classList.remove('active'));
        allBtn.classList.add('active');
        renderProducts();
    });

    const favBtn = document.createElement('div');
    favBtn.className = 'cat';
    favBtn.textContent = '❤️ Favorites';
    favBtn.addEventListener('click', () => {
        document.querySelectorAll('.cat').forEach(c => c.classList.remove('active'));
        favBtn.classList.add('active');
        renderProducts('FAVORITES');
    });
    categoriesEl.appendChild(favBtn);

    cats.forEach(c => {
        const el = document.createElement('div');
        el.className = 'cat';
        el.textContent = c;
        el.addEventListener('click', () => {
            document.querySelectorAll('.cat').forEach(cc => cc.classList.remove('active'));
            el.classList.add('active');
            renderProducts(c);
        });
        categoriesEl.appendChild(el);
    });
}

// Render Products
function renderProducts(filterCat, searchQ) {
    const q = (searchQ || searchInput.value || '').toLowerCase();
    productsEl.innerHTML = '';

    let list = filterCat === 'FAVORITES'
        ? products.filter(p => favorites.includes(p.id))
        : products.filter(p => {
            if (filterCat && filterCat !== 'All' && p.category !== filterCat) return false;
            if (q && !(p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q))) return false;
            return true;
        });

    list.forEach(p => {
        const cartItem = cart.find(c => c.id === p.id);
        const isFav = favorites.includes(p.id);

        const div = document.createElement('div');
        div.className = 'product';
        div.innerHTML = `
            <div class="p-top">
                <div style="position:relative;width:100%">
                    <div class="p-image">
                        <img src="${p.image || 'https://via.placeholder.com/150?text=' + encodeURIComponent(p.name)}" 
                             alt="${p.name}" 
                             onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image'">
                    </div>
                    <button class="fav-btn ${isFav ? 'active' : ''}" onclick="toggleFavorite(${p.id})" 
                            style="position:absolute;top:8px;right:8px;background:rgba(255,255,255,0.9);border:none;font-size:18px;padding:6px 8px;border-radius:6px;cursor:pointer">❤</button>
                </div>
                <div>
                    <div class="p-name">${p.name}</div>
                    <div class="p-qty">${p.stock > 0 ? p.stock + ' left' : 'Out of stock'}</div>
                </div>
            </div>
            <div class="p-bottom">
                <div class="price">₹${p.price}</div>
                ${cartItem
                ? `<div class="qty-control">
                         <button class="qty-btn" onclick="changeCartQty(${p.id},-1)">−</button>
                         <div class="qty-val">${cartItem.qty}</div>
                         <button class="qty-btn" onclick="changeCartQty(${p.id},1)">+</button>
                       </div>`
                : `<button class="add-small" onclick="addToCart(${p.id})" ${p.stock <= 0 ? 'disabled' : ''}>Add</button>`
            }
            </div>
        `;
        productsEl.appendChild(div);
    });
}

// Toggle Favorite
function toggleFavorite(id) {
    if (favorites.includes(id)) {
        favorites = favorites.filter(f => f !== id);
        showToast('Removed from favorites', 'info');
    } else {
        favorites.push(id);
        showToast('Added to favorites', 'success');
    }
    localStorage.setItem('gg_favorites', JSON.stringify(favorites));
    renderProducts();
}

function findProduct(id) { return products.find(p => p.id === id); }

// Cart Functions
function addToCart(id) {
    const p = findProduct(id);
    if (!p || p.stock <= 0) {
        showToast('Product out of stock', 'error');
        return;
    }

    const item = cart.find(c => c.id === id);
    if (item) {
        if (item.qty < p.stock) {
            item.qty++;
        } else {
            showToast(`Maximum ${p.stock} available`, 'error');
            return;
        }
    } else {
        cart.push({ id: p.id, name: p.name, price: p.price, qty: 1 });
    }

    updatePopbar();
    renderProducts();
    saveState();
}

function changeCartQty(id, delta) {
    const item = cart.find(c => c.id === id);
    if (!item) return;

    // Check max stock before increasing
    if (delta > 0) {
        const product = findProduct(id);
        if (product && item.qty >= product.stock) {
            showToast(`Maximum ${product.stock} available`, 'error');
            return;
        }
    }

    item.qty += delta;
    if (item.qty <= 0) {
        cart = cart.filter(c => c.id !== id);
    }

    updatePopbar();
    renderProducts();
    renderCartItems(); // Re-render cart items
    saveState();
}

function updatePopbar() {
    const qty = cart.reduce((s, i) => s + i.qty, 0);
    const total = cart.reduce((s, i) => s + i.qty * i.price, 0);
    popQty.textContent = qty;
    popTotal.textContent = total;
    topCartCount.textContent = qty;
    openCartBtn.disabled = qty === 0;
    openCartBtn.style.opacity = qty === 0 ? '0.6' : '1';
}

// Cart Page
function openCart() {
    renderCartItems();

    // Pre-fill form from saved profile
    if (userProfile) {
        custName.value = userProfile.name || '';
        custPhone.value = userProfile.phone || '';
        custRoom.value = userProfile.room || '';
    }

    cartPage.style.display = 'flex';
}

function closeCart() {
    cartPage.style.display = 'none';
}

function renderCartItems() {
    cartItemsEl.innerHTML = '';
    if (cart.length === 0) {
        cartItemsEl.innerHTML = '<div class="small-muted">Cart is empty</div>';
    }
    cart.forEach(item => {
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <div class="left">
                <div style="width:44px;height:44px;border-radius:8px;background:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;border:1px solid rgba(0,0,0,0.03)">${item.name.charAt(0)}</div>
                <div style="margin-left:10px">
                    <div style="font-weight:800">${item.name}</div>
                    <div class="small-muted">₹${item.price} x ${item.qty}</div>
                </div>
            </div>
            <div class="cart-actions">
                <button onclick="changeCartQty(${item.id}, -1)" class="qty-btn">-</button>
                <div style="min-width:30px;text-align:center">${item.qty}</div>
                <button onclick="changeCartQty(${item.id}, 1)" class="qty-btn">+</button>
            </div>
        `;
        cartItemsEl.appendChild(div);
    });
    const total = cart.reduce((s, i) => s + i.qty * i.price, 0);
    cartTotalEl.textContent = total;
    updatePopbar();
}

// Confirm Reservation
async function confirmReservation() {
    if (cart.length === 0) return showToast('Cart is empty', 'error');

    const name = custName.value.trim();
    const phone = custPhone.value.trim();
    const room = custRoom.value.trim();

    if (!name || !phone || !room) {
        return showToast('Enter name, phone & room', 'error');
    }

    if (!/^[a-zA-Z\s]+$/.test(name)) {
        return showToast('Name must contain only letters', 'error');
    }

    if (!/^\d{10}$/.test(phone)) {
        return showToast('Phone must be exactly 10 digits', 'error');
    }

    // Auto-save profile for next time
    userProfile = {
        name: name,
        phone: phone,
        room: room,
        verified: false
    };
    localStorage.setItem('gg_user_profile', JSON.stringify(userProfile));

    try {
        const total = cart.reduce((s, i) => s + i.qty * i.price, 0);

        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                items: cart.map(item => ({
                    productId: item.id,
                    name: item.name,
                    price: item.price,
                    qty: item.qty
                })),
                customerName: name,
                phoneNumber: phone,
                roomNumber: room,
                notes: ''
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (data.existingOrderId) {
                // User already has an active order
                showToast('You already have an active order!', 'error');
                // Try to load the existing order
                const existingRes = await fetch(`/api/orders/${data.existingOrderId}`);
                if (existingRes.ok) {
                    const existingOrder = await existingRes.json();
                    const until = new Date(existingOrder.expiresAt).getTime();
                    activeReservation = {
                        id: existingOrder.orderId,
                        items: existingOrder.items,
                        total: existingOrder.totalAmount,
                        until,
                        name: existingOrder.customerName,
                        phone: existingOrder.phoneNumber,
                        room: existingOrder.roomNumber
                    };
                    saveState();
                    showReservation();
                    showReservationBanner();
                    startReservationTimer();
                    openReservationDetails();
                }
                return;
            }
            return showToast(data.error || 'Order failed', 'error');
        }

        const until = Date.now() + 15 * 60 * 1000;
        activeReservation = {
            id: data.orderId,
            items: JSON.parse(JSON.stringify(cart)),
            total,
            until,
            name,
            phone,
            room
        };

        let sales = JSON.parse(localStorage.getItem('gg_sales') || '[]');
        sales.push({
            total,
            items: activeReservation.items,
            time: Date.now()
        });
        localStorage.setItem('gg_sales', JSON.stringify(sales));
        renderRecentOrders();

        cart = [];
        await loadProducts();
        renderProducts();
        renderCartItems();
        updatePopbar();
        showReservation();
        showReservationBanner();
        startReservationTimer();
        saveState();

        showToast(`Order ${activeReservation.id} confirmed!`, 'success');

        setTimeout(() => {
            closeCart();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 500);

    } catch (error) {
        console.error('Order creation error:', error);
        showToast('Failed to create order: ' + (error.message || 'Unknown error'), 'error');
    }
}

function showReservation() {
    if (!activeReservation) {
        reservationInfo.textContent = '';
        return;
    }
    reservationInfo.innerHTML = `<div><strong>Order ID:</strong> ${activeReservation.id}</div><div class="small-muted">Reserved for ${activeReservation.name} • Room ${activeReservation.room}</div><div style="margin-top:8px" id="resTimer">Time left: --:--</div>`;
}

function showReservationBanner() {
    if (!activeReservation) return;

    const banner = document.getElementById('reservationBanner');
    if (!banner) return;

    document.getElementById('bannerOrderId').textContent = activeReservation.id;
    document.getElementById('bannerTimer').textContent = '--:--';

    banner.style.display = 'block';
    const viewBtn = document.getElementById('viewReservationBtn');
    if (viewBtn) {
        viewBtn.onclick = () => {
            openReservationDetails();
            cartPage.style.display = 'flex';
        };
    }
}

function hideReservationBanner() {
    const banner = document.getElementById('reservationBanner');
    if (banner) banner.style.display = 'none';
}

function openReservationDetails() {
    if (!activeReservation) return;
    cartItemsEl.innerHTML = '';
    activeReservation.items.forEach(item => {
        const pdiv = document.createElement('div');
        pdiv.className = 'cart-item';
        pdiv.innerHTML = `
            <div class="left">
                <div style="width:36px;height:36px;border-radius:6px;background:#f3f4f6;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px">${item.name.charAt(0)}</div>
                <div style="margin-left:8px">
                    <div style="font-weight:700;font-size:14px">${item.name}</div>
                    <div style="font-size:12px;color:#6b7280">₹${item.price} × ${item.qty}</div>
                </div>
            </div>
            <div style="font-weight:700;font-size:14px">₹${item.price * item.qty}</div>
        `;
        cartItemsEl.appendChild(pdiv);
    });
    cartTotalEl.textContent = activeReservation.total;
    reservationInfo.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;padding:12px;background:#ecfdf5;border-radius:8px;border:1px solid #10b981;margin-bottom:12px">
            <div style="flex:1">
                <div style="font-weight:700;font-size:14px;color:#059669">Order ${activeReservation.id}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:2px">${activeReservation.name} • Room ${activeReservation.room}</div>
            </div>
            <div id="resTimer" style="font-size:13px;font-weight:700;color:#059669;background:white;padding:6px 10px;border-radius:6px">--:--</div>
        </div>
        <button onclick="cancelOrder()" style="width:100%;padding:10px;background:#dc2626;color:white;border:none;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer">Cancel Order</button>
    `;
}

async function cancelOrder() {
    if (!activeReservation) return;
    if (!confirm(`Cancel order ${activeReservation.id}?`)) return;

    try {
        const response = await fetch(`/api/orders/${activeReservation.id}/cancel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: 'Customer cancellation' })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to cancel order');
        }

        activeReservation = null;
        showReservation();
        hideReservationBanner();
        saveState();
        closeCart();

        await loadProducts();
        renderProducts();

        window.scrollTo({ top: 0, behavior: 'smooth' });
        showToast('Order cancelled successfully', 'info');
    } catch (error) {
        console.error('Cancel order error:', error);
        showToast('Cancellation failed: ' + error.message, 'error');
    }
}

window.cancelOrder = cancelOrder;

function startReservationTimer() {
    if (reserveInterval) clearInterval(reserveInterval);
    reserveInterval = setInterval(() => {
        if (!activeReservation) {
            clearInterval(reserveInterval);
            return;
        }
        const rem = activeReservation.until - Date.now();
        if (rem <= 0) {
            clearInterval(reserveInterval);
            expireReservation();
        } else {
            const m = Math.floor(rem / 60000);
            const s = Math.floor((rem % 60000) / 1000);
            const txt = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
            const el = document.getElementById('resTimer');
            if (el) el.textContent = 'Time left: ' + txt;
            const b = document.getElementById('bannerTimer');
            if (b) b.textContent = txt;
        }
    }, 1000);
}

function expireReservation() {
    if (!activeReservation) return;
    showToast('Reservation expired', 'error');
    activeReservation = null;
    showReservation();
    renderProducts();
    hideReservationBanner();
    saveState();
}

// Event Listeners
openCartBtn.addEventListener('click', openCart);
if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
topCartBtn.addEventListener('click', openCart);
reserveBtn.addEventListener('click', confirmReservation);
if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

// Profile button removed - profile is auto-created from cart form
const profileBtn = document.getElementById('profileBtn');
if (profileBtn) {
    // Repurpose profile button to show user orders
    profileBtn.addEventListener('click', () => {
        openCart();
    });
}

const viewReservationBtn = document.getElementById('viewReservationBtn');
if (viewReservationBtn) {
    viewReservationBtn.addEventListener('click', () => {
        openReservationDetails();
        cartPage.style.display = 'flex';
    });
}

const openCartEl = document.getElementById('openCart');
if (openCartEl) openCartEl.addEventListener('click', openCart);

searchInput.addEventListener('input', () => renderProducts());
if (searchClear) searchClear.addEventListener('click', () => {
    searchInput.value = '';
    renderProducts();
});

// Admin Secret URL Redirect
if (window.location.pathname === '/admin' || window.location.hash === '#admin') {
    window.location.href = '/admin.html';
}

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        document.getElementById('themeToggle').textContent = darkMode ? '☀️' : '🌙';
        loadState();
        products = JSON.parse(JSON.stringify(products));
        userProfile = JSON.parse(localStorage.getItem('gg_user_profile') || 'null');
        renderOffers();
        startOfferCarousel();
        renderCategories();
        renderProducts();
        renderRecentOrders();
        updatePopbar();
        await loadProducts();
        renderProducts();
        renderCategories();
        await loadActiveOrder();
        renderRecentOrders();
    } catch (e) {
        alert('Init error: ' + e);
    }
});

// Ripple Effect
document.addEventListener('click', function (e) {
    const btn = e.target.closest('button');
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    ripple.style.left = (e.clientX - rect.left) + 'px';
    ripple.style.top = (e.clientY - rect.top) + 'px';
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
});
