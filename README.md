# PGEL-SAT
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php) 
> A tractable Probabilistic Graphic EL++ SAT solver

## Install the dependencies
```bash
pip3 install -r requirements.txt
```

## Create an OWL file with probabilities
Add a `rdfs:comment` to `owl:Thing` concept for each probability restriction in PBox. There **must** be the header `#! pbox-restriction` in these comments. 

Then, the next lines will be a pair with the `pbox-id` of the axiom and its `coefficient` and the **last two lines** must be the `sign` of the restriction (`==`, `<=` or `>=`) and the `value` (or right-hand side) of the restriction.  

> ### For example: 
> 
> Supose you want to express 
>
> -1 * P(Ax0) + 1 * P(Ax1) = 0.05
>
>  3 * P(Ax2) = 0.7
>
> You need to add **two** `rdfs:comment`s to `owl:Thing`, with the content  
> ```
> #! pbox-restriction
> 0 -1 
> 1  1
> ==
> 0.05
> ```
> and
> ```
> #! pbox-restriction
> 2 3 
> ==
> 0.7
> ```

Add a `rdfs:comment` to every axiom in the PBox. There **must** be the header `#! pbox-id` in these comments, followed, in the next line, for its unique `id`.

> ### For example: 
> 
> Supose some axiom `Ax0` is in PBox. 
> You need to add one `rdfs:comment`s to this, with the content  
> ```
> #! pbox-id
> 0 
> ```

## Usage
The `<inputfile>` will be your OWL file with probabilistic restrictions. 

```bash
python3 pgel_sat.py <inputfile> [--trace]
```
## 