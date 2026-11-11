// Prices are whole cents.
export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}
