A Kochen-Specker System has at least 21 vertices
------------------------------------------------

Bas Westerbaan (bwesterb@cs.ru.nl)
Sander Uijlen (suijlen@cs.ru.nl)

Abstract
========
At the heart of the Conway's Free Will theorems and Kochen and
Specker's argument against non-contextual hidden variable theories
is the existence of a Kochen-Specker (KS) system: a set of points
on the sphere that has no {0, 1}-coloring such that at most one of
two orthogonal points are colored 1 and of three pairwise orthogonal
points exactly one is colored 1. In public lectures, Conway
encouraged the search for small KS systems. At the time of writing,
the smallest known KS system has 31 vectors.  Arends, Ouaknine and
Wampler have shown that a KS system has at least 18 vectors, by
reducing the problem to the existence of graphs with a topological
embeddability and non-colorability property. The bottleneck in their
search proved to be the sheer number of graphs on more than 17
vertices and deciding embeddability.  Continuing their effort, we
prove a restriction on the class of graphs we need to consider and
develop a more practical decision procedure for embeddability to
improve the lower bound to 21.

This repository
===============

This repository contains the

 * LaTeX sourcecode of the preprint (under `/paper`);
 * source code used for the computation (under `/code`,
   in particular `/code/comp<n>.py`) and
 * source code of the website kochen-specker.info (under `/site`).
    * First, in `/code`, run `python generateSite.py`.
    * Then, in  `/site`, run `jekyll build`.
    * Find the site in `/site/_site`.