import { test } from "node:test";
import assert from "node:assert/strict";
import { subtotal } from "../src/cart.js";

test("subtotal adds price times quantity", () => {
  assert.equal(subtotal([{ price: 48000, quantity: 1 }, { price: 22000, quantity: 2 }]), 92000);
});
