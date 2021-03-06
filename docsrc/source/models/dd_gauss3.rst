.. highlight:: python
.. _dd_gauss3:


************************
:mod:`dd_gauss3`
************************

.. autofunction:: deerlab.dd_models.dd_gauss3

Model
=========================================

:math:`P(r) = a_1\sqrt{\frac{2}{\pi}}\frac{1}{\sigma_1}\exp\left(-\frac{(r-\left<r_1\right>)^2}{\sigma_1^2}\right) + a_2\sqrt{\frac{2}{\pi}}\frac{1}{\sigma_2}\exp\left(-\frac{(r-\left<r_2\right>)^2}{\sigma_2^2}\right) + a_3\sqrt{\frac{2}{\pi}}\frac{1}{\sigma_3}\exp\left(-\frac{(r-\left<r_3\right>)^2}{\sigma_3^2}\right)`

with :math:`\sigma_i = \mathrm{FWHM}_i/\sqrt{2ln(2)}`

================ ======================== ========= ======== ========= ===================================
 Variable         Symbol                    Default   Lower    Upper       Description
================ ======================== ========= ======== ========= ===================================
``param(1)``     :math:`\left<r_1\right>`     2.5     1.0        20         1st Gaussian center distance
``param(2)``     :math:`\mathrm{FWHM}_1`      0.5     0.2        5          1st Gaussian FWHM
``param(3)``     :math:`a_1`                  0.3     0          1          1st Gaussian amplitude
``param(4)``     :math:`\left<r_2\right>`     3.5     1.0        20         2nd Gaussian center distance
``param(5)``     :math:`\mathrm{FWHM}_2`      0.5     0.2        5          2nd Gaussian FWHM
``param(6)``     :math:`a_2`                  0.3     0          1          2nd Gaussian amplitude
``param(7)``     :math:`\left<r_3\right>`     5.0     1.0        20         3rd Gaussian center distance
``param(8)``     :math:`\mathrm{FWHM}_3`      0.5     0.2        5          3rd Gaussian FWHM
``param(9)``     :math:`a_3`                   0.3     0          1          3rd Gaussian amplitude
================ ======================== ========= ======== ========= ===================================


Example using default parameters:

.. image:: ../images/model_dd_gauss3.png
   :width: 650px
