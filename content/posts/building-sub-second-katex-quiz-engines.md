---
title: "Architecting Sub-Second KaTeX Quiz Engines: Zero-Latency Physics CBT"
date: "2026-08-28"
tags: ["EdTech", "WebDev", "Performance", "KaTeX", "JavaScript"]
description: "How we eliminated DOM reflow bottlenecks and achieved 60fps scrolling across 180+ math-heavy questions in a JEE Advanced computer-based testing engine."
slug: "building-sub-second-katex-quiz-engines"
reading_time: "5 min read"
---

When building computer-based test (CBT) engines for national-level competitive examinations like JEE Advanced or NEET, raw execution speed is not a luxury—it is an accessibility and fairness requirement. 

A standard 3-hour mock examination features 180 comprehensive questions spanning physics, chemistry, and mathematics. Each question contains complex mathematical notation, vector expressions, matrix determinants, and inline Greek superscripts:

$$\oint_{\partial \Sigma} \vec{B} \cdot d\vec{\ell} = \mu_0 \left( I_{\text{enc}} + \varepsilon_0 \frac{d\Phi_E}{dt} \right)$$

If an exam interface stutters while a candidate navigates questions, mental focus breaks. Here is the architectural blueprint we implemented to render hundreds of dynamic LaTeX equations with zero perceived latency.

---

## 1. The Bottleneck: Unconstrained DOM Ingestion

In early prototypes, standard Markdown-to-HTML engines would run `renderMathInElement(document.body)` on every question transition. 

This approach is fatal for performance due to **Cumulative Layout Shift (CLS)** and **Forced Synchronous Layouts**:

```
[Fetch Question Payload] 
       ↓ 
[Raw String Injection into innerHTML] 
       ↓ 
[Global KaTeX Walker parses 1,000+ nodes] 
       ↓ 
[Forced Recalculate Style & Reflow] ---> 280ms dropped frames!
```

When 50 candidate equations are evaluated on every click, the browser thread locks up for 200–300ms, causing noticeable cursor lag and battery drain on low-spec client machines.

---

## 2. Solution: Worker-Thread Precompilation & AST Memoization

KaTeX has a massive advantage over MathJax: **KaTeX is synchronous and can generate pure HTML strings directly on a Web Worker without touching the DOM**.

### Implementation Pattern

Instead of passing unparsed LaTeX strings to the main thread:

```javascript
// worker-katex.js
importScripts('https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js');

self.onmessage = function(e) {
  const { questionId, rawLatexSegments } = e.data;
  
  const renderedHtml = rawLatexSegments.map(item => {
    return {
      id: item.id,
      html: katex.renderToString(item.formula, {
        displayMode: item.isBlock,
        throwOnError: false
      })
    };
  });

  self.postMessage({ questionId, renderedHtml });
};
```

By offloading string tokenization and tree creation to a dedicated background worker, the main thread remains completely idle (0ms layout freeze).

---

## 3. Virtualized DOM Node Pooling

In an interactive CBT palette containing 180 questions, keeping all questions active in the live DOM tree inflates memory consumption to over 150MB:

- **Naïve Approach**: 180 DOM nodes $\times$ 40 KaTeX sub-elements = 7,200 active elements.
- **Virtualized Windowing**: Only **3 active question slides** reside in the DOM at any given moment:
  1. Slide $N-1$ (Pre-rendered for instantaneous swipe back)
  2. Slide $N$ (Active question in view)
  3. Slide $N+1$ (Pre-rendered for immediate forward progression)

When the student navigates from Question 14 to Question 15, Question 13 is recycled into a dormant memory cache, maintaining an unwavering 60 frames per second.

```
[ Buffer Slide N-1 ] <--- [ Active Slide N ] ---> [ Buffer Slide N+1 ]
      (Cached)                 (Rendered)               (Pre-warmed)
```

---

## 4. Offline First: IndexedDB Blob Caching

Physics diagrams and question payloads are structured as content-addressable blobs:

$$\text{Hash} = \text{SHA-256}(\text{Question Markdown} + \text{Diagram SVG})$$

Upon test initialization, the entire test bundle is cached into IndexedDB:

```javascript
async function loadOfflineTest(testId) {
  const db = await openDatabase('smaphysics_cbt', 1);
  const cachedTest = await db.get('tests', testId);
  
  if (cachedTest) {
    console.log('[CBT Engine] Initialized in 12ms from local cache.');
    return cachedTest;
  }
  
  const response = await fetch(`/api/tests/${testId}.json`);
  const freshData = await response.json();
  await db.put('tests', freshData, testId);
  return freshData;
}
```

Even if the examination center loses internet connectivity during the test, the test continues uninterrupted, and candidate responses are queued in `localStorage` until the network recovers.

---

## Conclusion

Speed in educational tools is not just an aesthetic consideration—it directly impacts learner confidence and exam outcomes. Combining pure vanilla JavaScript, Web Worker pre-compilation, and KaTeX produces an educational client that is instantaneous, fault-tolerant, and accessible on any device.
