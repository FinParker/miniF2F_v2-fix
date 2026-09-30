import Mathlib

-- A global equivalence is false; negating every individual instance is wrong.
example : ¬ (∀ a b : ℤ, (Even a ∧ Even b) ↔ 8 ∣ a^2+b^2) := by
  intro h
  have hx := h 0 2
  norm_num at hx

-- The inverse congruence has the intended nonvacuous solution.
example : Nat.Coprime 6 43 ∧ Nat.ModEq 43 (6 * 6^2) 1 := by decide

-- Boundary case for the non-strict inequality.
example : (1 : ℝ) ^ ((1 : ℝ) / 1) ≤ 2 - 1 / 1 := by norm_num

-- Distinct-root guard rules out the reported double-root counterexample.
example : ((-(1/2 : ℝ))^2 + (-(1/2 : ℝ)) * (-(1/2 : ℝ)) - 1/2) = 0 := by norm_num
example : ¬ ((-(1/2 : ℝ)) ≠ -(1/2 : ℝ)) := by simp

-- Natural subtraction can hide a negative difference; addition equations cannot.
example : (1 - 2 - 3 : ℕ) = 0 := by decide
example : ¬ ((1 : ℕ) = 2+3 ∨ (1 : ℕ) = 2+3+1) := by decide

example : ((139 - 1) % 11 + 1 : ℕ) = 7 := by decide
example : (1/3 : ℝ) * (30 * (13/2)) = 65 := by norm_num

-- The old algebra_275 statement is vacuous; the repaired theorem has a real proof.
example : (11 : ℝ) ^ (1/4) = 1 := by norm_num
example (x : ℝ) (h : ((11 : ℝ) ^ (1/4 : ℝ)) ^ (3*x-3) = 1/5) :
    ((11 : ℝ) ^ (1/4 : ℝ)) ^ (6*x+2) = 121/25 := by
  have hp : 0 < (11 : ℝ) ^ (1/4 : ℝ) := Real.rpow_pos_of_pos (by norm_num) _
  have h8 : ((11 : ℝ) ^ (1/4 : ℝ)) ^ (8 : ℝ) = 121 := by
    rw [← Real.rpow_mul (by norm_num : (0 : ℝ) ≤ 11)]
    norm_num [Real.rpow_two]
  calc
    _ = ((11 : ℝ) ^ (1/4 : ℝ)) ^ ((3*x-3)*2+8) := by congr 1; ring
    _ = (((11 : ℝ) ^ (1/4 : ℝ)) ^ (3*x-3)) ^ (2 : ℝ) *
        ((11 : ℝ) ^ (1/4 : ℝ)) ^ (8 : ℝ) := by
          rw [Real.rpow_add hp, Real.rpow_mul (le_of_lt hp)]
    _ = _ := by rw [h, h8]; norm_num [Real.rpow_two]

-- k=m=n=2 satisfies the original IMO hypotheses but breaks the old product.
example : Nat.Prime (2+2+1) ∧ 2+1 < 2+2+1 := by decide
example : ¬ ((∏ i in Finset.Icc (1 : ℕ) 2, i*(i+1)) ∣
    (∏ i in Finset.Icc (1 : ℕ) 2, (2+i)*(2+i+1)) - 2*(2+1)) := by decide
example : (∏ i in Finset.Icc (1 : ℕ) 2, i*(i+1)) ∣
    (∏ i in Finset.Icc (1 : ℕ) 2, ((2+i)*(2+i+1) - 2*(2+1))) := by decide
