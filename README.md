## Example

![Epicycle example](epicycles.gif)

## How it works

The first time I saw one of those epicycle drawing animations (https://www.youtube.com/watch?v=QVuU2YCwHjw), I immediately knew it was 99% explained by Fourier decomposition, but it never *quite* made sense to me how the animation was generated. I finally dedicated a few minutes to understanding it, so I could implement it myself and experiment with it.

I found a lot of example implementations that were inscrutable due to being written in some frontend framework nonsense, in pygame, or whatever. I had a feeling that the core algorithm should fit inside a one-page function, so I had to figure that out. I ended up implementing it in about 30 lines of python/numpy/matplotlib; still highly readable in my opinion, and easier to grok when all the math and animation is done in a minimal way, all in one function. One useful reference, written in a style that made the process obvious to me: https://www.mathworks.com/matlabcentral/fileexchange/72821-drawing-with-fourier-epicycles.

In short:

<!--
latex in github markdown is neat, has some idiosyncracies...
- "*2*", previously indicating multiplication in a code block, breaks the renderer
- \sum with subscript and superscript doesn't work well for inline expressions
- "\\{" for curly braces, not sure if i've seen that elsewhere or just got lucky and guessed it
- how to define custom function names like \fft?
-->

1. Think of the 2d path as a "1d complex" signal

  - $x, y = f[n], g[n]$
  - $z[n] = f[n] + j*g[n]$
  - $Z[k] = \mathscr{F}\\{z[n]\\}$
   
2. Write the inverse transform in terms of the fourier series magnitudes and phases:
  - $z[n] = \sum Z[k] e^{j 2 \pi k n / N}$
  - $z[n] = \sum |Z[k]| \cdot e^{j \angle{Z}} \cdot e^{j 2 \pi k n / N}$

Where $|Z[k]|$ is the radius of the circle that spins with frequency k.

Normally, I think of the frequency `k` as the focus of this equation - the *frequency* identifying each of the "frequency components" - while Z[k] is the complex magnitude corresponding to that frequency `k`. This understanding is still accurate of course, but it obscures the next step:

3. Sort the components by *descending magnitude* instead of by *ascending frequency*, then draw the circles in that order.

This is a kind of nonlinear operation, something you would never consider as part of LTI theory (the basis of half of my education). It's not really useful in analysis of linear systems, or anything else that I'm aware of, it's just a neat trick for fancy-looking animations.

## Why I was curious
I found myself trying to figure out an algorithm for smoothing a polyline for CNC inlay cuts, which means it needs to be modified such that the cutting tool (a cylinder of diameter D, perhaps 1/4") is able to cut every section of it, from both sides. This means:

1. The radius of curvature should be greater than or equal to D/2 everywhere on the smoothed curve. (A single-sided toolpath would only require *signed curvature* to meet this criterion)
2. Both offset curves at distance D should never intersect the base curve.

While 2 is kind of tricky to manage in an analytical solution, I hoped I could at least find a robust, principle-based smoothing algorithm to satisfy 1. One thought I had was that I could use epicycle drawing, with a minimum size threshold on the circle radii; a kind of nonlinear filter that zeros out components based on their *magnitude* instead of their *frequency*. I realized pretty quickly that this by itself wouldn't work; the sum curve is not really constrained in curvature at all. But I was still curious about the epicycle drawing method, so I had to figure it out. Also, I wonder what kind of effects might be possible by using nonlinear filters like this, so I wanted a way to experiment.
