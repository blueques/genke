(function () {
  const cart = [];
  const cartBody = document.getElementById("cart-items");
  const subtotalEl = document.getElementById("cart-subtotal");
  const vatEl = document.getElementById("cart-vat");
  const totalEl = document.getElementById("cart-total");
  const searchInput = document.getElementById("pos-search");
  const discountInput = document.getElementById("cart-discount");
  const tenderedInput = document.getElementById("cart-tendered");
  const paymentSelect = document.getElementById("cart-payment");
  const mpesaInput = document.getElementById("cart-mpesa-ref");
  const customerInput = document.getElementById("cart-customer");
  const checkoutBtn = document.getElementById("checkout-btn");

  if (!cartBody) return;

  const vatRate = parseFloat(cartBody.dataset.vatRate || "16") / 100;
  const taxInclusive = cartBody.dataset.taxInclusive === "true";

  function kes(value) {
    return "KES " + Number(value).toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function renderCart() {
    cartBody.innerHTML = "";
    let subtotal = 0;

    cart.forEach((item, idx) => {
      const lineTotal = item.price * item.qty;
      subtotal += lineTotal;
      const row = document.createElement("div");
      row.style.cssText = "display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #e2e8f0;";
      row.innerHTML = `
        <div>
          <div style="font-weight:600;font-size:13px;">${item.name}</div>
          <div class="mono" style="font-size:12px;color:#64748b;">${kes(item.price)} x ${item.qty}</div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button type="button" class="btn" data-dec="${idx}">-</button>
          <button type="button" class="btn" data-inc="${idx}">+</button>
        </div>
      `;
      cartBody.appendChild(row);
    });

    const discount = parseFloat(discountInput?.value || "0") || 0;
    const net = Math.max(0, subtotal - discount);
    const vat = taxInclusive ? net - net / (1 + vatRate) : net * vatRate;
    const total = taxInclusive ? net : net + vat;

    subtotalEl.textContent = kes(subtotal);
    vatEl.textContent = kes(vat);
    totalEl.textContent = kes(total);
  }

  document.querySelectorAll(".product-card").forEach((card) => {
    card.addEventListener("click", () => {
      const id = Number(card.dataset.id);
      const name = card.dataset.name;
      const price = parseFloat(card.dataset.price);
      const stock = Number(card.dataset.stock);
      const existing = cart.find((c) => c.id === id);
      if (existing) {
        if (existing.qty < stock) existing.qty += 1;
      } else if (stock > 0) {
        cart.push({ id, name, price, qty: 1, stock });
      }
      renderCart();
    });
  });

  cartBody.addEventListener("click", (e) => {
    const dec = e.target.getAttribute("data-dec");
    const inc = e.target.getAttribute("data-inc");
    if (dec !== null) {
      const item = cart[Number(dec)];
      item.qty -= 1;
      if (item.qty <= 0) cart.splice(Number(dec), 1);
      renderCart();
    }
    if (inc !== null) {
      const item = cart[Number(inc)];
      if (item.qty < item.stock) item.qty += 1;
      renderCart();
    }
  });

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      const q = searchInput.value.toLowerCase();
      document.querySelectorAll(".product-card").forEach((card) => {
        const text = (card.dataset.name + " " + card.dataset.sku).toLowerCase();
        card.style.display = text.includes(q) ? "block" : "none";
      });
    });
  }

  if (discountInput) discountInput.addEventListener("input", renderCart);

  if (checkoutBtn) {
    checkoutBtn.addEventListener("click", async () => {
      if (cart.length === 0) return;
      const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
      const res = await fetch("/api/checkout/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({
          items: cart.map((c) => ({ product_id: c.id, quantity: c.qty, unit_price: c.price })),
          payment_method: paymentSelect.value,
          mpesa_ref: mpesaInput.value,
          customer_name: customerInput.value || "Walk-in Customer",
          discount_amount: parseFloat(discountInput.value || "0") || 0,
          amount_tendered: parseFloat(tenderedInput.value || "0") || 0,
        }),
      });
      const data = await res.json();
      if (res.ok && data.sale_id) {
        window.location.href = `/receipt/${data.sale_id}/`;
      } else {
        alert(data.error || "Checkout failed");
      }
    });
  }
})();
