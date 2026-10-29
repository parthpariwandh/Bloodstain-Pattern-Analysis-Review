# Bloodstain-Pattern-Analysis-Review

![Field](https://img.shields.io/badge/fluid%20dynamics-ML%20%2B%20imaging-navy)
![Companion](https://img.shields.io/badge/computational-companion-blue)
![University](https://img.shields.io/badge/Jadavpur%20University-ME-lightgrey)

Computational companion to the review: Bloodstain Pattern Analysis, a multidisciplinary reading of fluid dynamics, machine learning, and image processing. The repository name is unchanged.

Author: Parth Pariwandh, B.E. Mechanical Engineering, Jadavpur University. Prepared in connection with the short term research internship under Dr. Bahni Ray, IIT Delhi.

## What the code covers

- Exact 4-4-1 ANN surrogate for maximum spreading ratio
- Automated feature extraction from bloodstain images
- Probabilistic three dimensional region of origin
- Impact angle estimation
- Weber, Reynolds, and Ohnesorge utilities

## Papers connected

| Paper | Core problem | Method |
| --- | --- | --- |
| Choudhury et al. (2023) | Predicting beta max under roughness | Exact 4-4-1 ANN |
| Joris et al. (2014) | Impact angle | Active Bloodstain Shape Model |
| Attinger et al. (2019) | Region of origin with uncertainty | Probabilistic trajectories |
| Arthur et al. (2017) | Objective pattern description | Automated features |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Licence

MIT. Maintained by Parth Pariwandh, Jadavpur University.
