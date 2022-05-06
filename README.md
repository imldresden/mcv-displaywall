> **⚠ WARNING:**<br>
> The code in this project is no longer maintained.
> Use it with caution and check for vulnerabilities!

# DiViCo

The DiViCo (Distant Visualisation Control) prototype implements large-scale multiple coordinated views on a wall-sized interactive display. 
Users can interact with visualization views from both close proximity (touch input) as well from a distance (using a pointing approach with mobile devices).
The basic ideas and principles behind this research prototype can be found in our publication:

> Ricardo Langner, Ulrike Kister and Raimund Dachselt, "Multiple Coordinated Views at Large Displays for Multiple Users: Empirical Findings on User Behavior, Movements, and Distances" in IEEE
Transactions on Visualization and Computer Graphics, vol. 25, no. 1, 2018.
doi: [10.1109/TVCG.2018.2865235](https://doi.org/10.1109/TVCG.2018.2865235)

*Note: This prototype does not include all functionality presented in the research article. Due to their relevance for other projects, the node-link diagram and the lens tool are not included.*

**Project website**: Further information, photos, and videos can be found at
https://imld.de/mcv-displaywall/.

**Questions**: If you have any questions or you want to give feedback, please
contact Ricardo Langner
([institutional website](https://imld.de/en/our-group/team/ricardo-langner/),
[GitHub](https://github.com/derric)) or Marc Satkowski
([institutional website](https://imld.de/en/our-group/team/marc-satkowski/),
[GitHub](https://github.com/satkowski)).

## Installing and Running DiViCo

We use this prototyp with Python 2.7. After installing Python you need to install the following libraries:
  + enum34 (>= 1.1.6)
  + enum-compat (>= 0.0.2)
  + pyproj (>= 1.9.5.1)
  + numpy (>= 1.13.1)
  + scipy (>= 0.19.1)
  + pyOSC (>= 0.3.5b5294)
  + networkx (>= 2.1)
  + googlemaps (>= 2.5.1)
  + PyGLM (>=0.4.8b1)

Further it is necessary to install an additional library. This library is [libavg](https://www.libavg.de/site/) which 
allows us to handle touch input and gesture recognition.

## Development

This project is developed by [Marc Satkowski](https://github.com/satkowski), Ulrike Kister and
[Ricardo Langner](https://github.com/derric) at the
[Interactive Media Lab Dresden](https://imld.de/),
Technische Universität Dresden, Germany.
Further development information can be found via the
[develpoment guide](DEVELOPMENT.md).

If you want to contribute, please check the
[contribution guide](CONTRIBUTION.md), fork our project, create a feature
branch for your changes, and provide us with a pull request.

## Acknowledgements

This research prototype uses the
[Victim Based Crime Dataset](https://data.baltimorecity.gov/Public-Safety/BPD-Part-1-Victim-Based-Crime-Data/wsfq-mvij)
data set from [Baltimore](https://data.baltimorecity.gov/).
Further information can be found in the data set [README](assets/data/README.md).
