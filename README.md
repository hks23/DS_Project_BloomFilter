# DS_Project_BloomFilter

First commit - Harsh
First commit - Stella

# Bloom Filter – Probability & Optimal Parameters

## Parameters

| Symbol | Meaning |
|--------|---------|
| $m$ | Bit array size |
| $n$ | Number of inserted elements |
| $k$ | Number of hash functions |

---

## Step-by-Step Probability Derivation

### 1. Probability a single bit stays 0 after **one** hash

$$P = 1 - \frac{1}{m}$$

---

### 2. Probability a bit stays 0 after **k** hashes

$$P = \left(1 - \frac{1}{m}\right)^k$$

---

### 3. Probability a bit stays 0 after **n insertions** (total hash operations = $kn$)

$$P = \left(1 - \frac{1}{m}\right)^{kn}$$

For large $m$, this approximates to:

$$\left(1 - \frac{1}{m}\right)^{kn} \approx e^{-kn/m}$$

---

### 4. Probability a bit **is 1**

$$P(\text{bit is 1}) = \left(1 - e^{-kn/m}\right)$$

---

## False Positive Probability

- **Prob. one queried bit is 1:**

$$\left(1 - e^{-kn/m}\right)$$

- **Prob. all $k$ bits are 1** (false positive formula):

$$\boxed{P = \left(1 - e^{-kn/m}\right)^k}$$

---

## Optimal Number of Hash Functions

Starting from:

$$P(k) = \left(1 - e^{-kn/m}\right)^k$$

Take the natural log:

$$\ln(P) = k \ln\!\left(1 - e^{-kn/m}\right)$$

Differentiate with respect to $k$ and set to 0:

$$0 = \ln\!\left(1 - e^{-kn/m}\right) + \frac{nk}{m} \cdot \frac{e^{-nk/m}}{1 - e^{-nk/m}}$$

**Minimum occurs when:**

$$e^{-nk/m} = \frac{1}{2}$$

$$\frac{nk}{m} = \ln(2)$$

$$\boxed{k = \frac{m}{n} \ln(2)}$$

---

## Optimal Bit Array Size

Substituting $e^{-nk/m} = \frac{1}{2}$ back:

$$P = \left(1 - \frac{1}{2}\right)^k = \left(\frac{1}{2}\right)^k$$

$$\ln(P) = -k \ln(2) = -\frac{m}{n} \ln(2)^2$$

Solving for $m$:

$$\boxed{m = \frac{-n \ln(p)}{(\ln 2)^2}}$$

---

## Summary of Key Results

| Formula | Expression |
|---------|-----------|
| False positive probability | $P = \left(1 - e^{-kn/m}\right)^k$ |
| Optimal hash functions | $k = \dfrac{m}{n} \ln(2)$ |
| Optimal bit array size | $m = \dfrac{-n \ln(p)}{(\ln 2)^2}$ |