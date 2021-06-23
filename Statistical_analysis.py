"""Script for performing the statistical analysis of the measurements.

Author
------
Sebastian Lifka

Created
-------
Jun 21 2021

Modified
--------
Jun 21 2021
"""
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Comparison of the methods using different face filters.
# =============================================================================
# Measurement series ATI-penetrometer
ati_penetrometer = np.asarray([19.86, 48.58, 61.89, 48.06, 7.83, 19.59, 1.6])

# Measurement series scale
scale1 = np.asarray([22.35, 49.41, 51.76, 40, 9.41, 21.18, 2.35])
scale2 = np.asarray([21.18, 47.06, 54.12, 37.65, 5.88, 24.71, 1.18])
scale3 = np.asarray([17.65, 48.24, 57.65, 36.47, 8.24, 18.82, 1.18])

# Measurement series light scattering detector
scatter1 = np.asarray([26, 48, 44, 12, 15, 23, 4])
scatter2 = np.asarray([23, 46, 45, 34, 17, 21, 1])
scatter3 = np.asarray([24, 42, 62, 21, 14, 23, 2])
scatter4 = np.asarray([35, 72, 21, 31, 2, 31, 5])
scatter5 = np.asarray([32, 72, 30, 32, 1, 32, 0])
scatter6 = np.asarray([32, 58, 43, 33, 2, 38, 3])

# Measurment series new light scattering detector
scatter1_new = np.asarray([23.9, 52.9, 4.8, 0.1])
scatter2_new = np.asarray([20.2, 32.1, 8.4, 0.4])
scatter3_new = np.asarray([15.1, 61.2, 5.2, 0.1])
scatter4_new = np.asarray([26, 77.1, 7.2, 0.8])
scatter5_new = np.asarray([17.6, 82.7, 6.9, 0.1])
scatter6_new = np.asarray([19.9, 79.9, 5.4, 0.1])

mask = ['Spunbond', 'Cotton', 'CUBO', 'Surgery Facemask', 'KN95',
        'Spunbond + Cotton', 'FFP2']
marl_er = ['o', '<', '>', 'x', '^', 'v', 'P']

# Mean values and standard deviation of the scatter method
means_scatter = np.mean([scatter1, scatter2, scatter3, scatter4, scatter5,
                         scatter6], axis=0)
std_scatter = np.std([scatter1, scatter2, scatter3, scatter4, scatter5,
                      scatter6], axis=0, ddof=1)
# Mean values and standard deviation of the scale method
means_scale = np.mean([scale1, scale2, scale3], axis=0)
std_scale = np.std([scale1, scale2, scale3], axis=0, ddof=1)
# Correlation coefficient
r_scatter = np.corrcoef(ati_penetrometer, means_scatter)
r_scale = np.corrcoef(ati_penetrometer, means_scale)

# Plot measurement results
plt.figure(1, figsize=[6.4, 9.6])
# Subplot scatter method
plt.subplot(212)
for i in range(7):
    plt.errorbar(ati_penetrometer[i], means_scatter[i], std_scatter[i],
                 marker=marl_er[i], capsize=3, elinewidth=1,
                 label=mask[i], linestyle='None')
    plt.plot([0, 70], [0, 70], 'k:', linewidth=1)

plt.xlabel('penetration in % ATI-penetrometer')
plt.ylabel('penetration in % scatter method')
plt.legend()
plt.grid(True)
plt.text(-11, 74, 'B', fontsize=14)
plt.text(60.5, 0.5, 'r = %.3f' % round(r_scatter[0, 1], 3), fontsize=10)
plt.tight_layout()

# Subplot scale method
plt.subplot(211)
for i in range(7):
    plt.errorbar(ati_penetrometer[i], means_scale[i], std_scale[i],
                 marker=marl_er[i],
                 capsize=3, elinewidth=1, label=mask[i], linestyle='None')
    plt.plot([0, 70], [0, 70], 'k:', linewidth=1)

plt.xlabel('penetration in % ATI-penetrometer')
plt.ylabel('penetration in % scale method')
plt.legend()
plt.grid(True)
plt.text(-11, 74, 'A', fontsize=14)
plt.text(60.5, 0.5, 'r = %.3f' % round(r_scale[0, 1], 3), fontsize=10)
plt.tight_layout()
plt.savefig('comparison.eps', dpi=300)

# =============================================================================
# Relative change of the penetration of different filters after being
# discharged.
# =============================================================================
# Measurement results relative change
relative_change = np.asarray([20 / 19, 46 / 44, 46 / 34, 17 / 9, 15 / 9])*100
errors_relative_change = [7, 6, 12, 15, 25]


mask_decharge = ['Spunbond', 'CUBO', 'Surgery Facemask', 'KN95', 'KN95 used']
pos = np.arange(len(mask_decharge))

# Plot measurement results
fig, ax = plt.subplots()
plt.figure(2)
ax.barh(pos, relative_change, xerr=errors_relative_change, align='center',
        color='tab:blue', edgecolor='black', capsize=3, zorder=3)
ax.set_yticks(pos)
ax.set_yticklabels(mask_decharge)
ax.plot([100, 100], [-.5, 4.5], linestyle=':', color='tab:orange', linewidth=2,
        zorder=6)
plt.xlabel('increase of penetration after decharging in %')
plt.tight_layout()
plt.grid(True, axis='x')
plt.savefig('relative_changes.eps', dpi=300)

# =============================================================================
# Penetration of different lots of KN95 face masks.
# =============================================================================
# Meaaurement results different lots
values_different_lots_plaine = np.asarray([5.68, 7.44, 3.76, 12.16, 4.48, 1.2,
                                           2.72])
values_different_lots_embossed = np.asarray([5.84, 7.12, 4.16, 17.28, 4.4,
                                             1.28, 2.64])
errors_different_lots_plaine = [1, 1.3, 1.2, 3.5, 1.5, 0.5, 1]
errors_different_lots_embossed = [1.3, 1.2, 1.6, 4, 1.75, 0.6, 1]
pos = np.arange(len(values_different_lots_plaine))
# print(pos)

fig, ax = plt.subplots()
plt.figure(3)
ax.bar(8-pos*2-.4, values_different_lots_plaine,
       yerr=errors_different_lots_plaine, align='center', color='gray',
       edgecolor='black', label='plaine', capsize=3, zorder=3)
ax.bar(8-pos*2+.4, values_different_lots_embossed,
       yerr=errors_different_lots_embossed, align='center', color='tab:blue',
       edgecolor='black', label='embossed', capsize=3, zorder=3)
plt.legend()

plt.xlabel('KN95 lot number')
plt.ylabel('penetration in %')

ax.set_xticklabels(['0', '1', '2', '3', '4', '5', '6', '7'])
plt.grid(True, axis='y')
plt.show()
plt.savefig('different_lots.eps', dpi=300)

# =============================================================================
# Comparison of the new scatter detector with the ATI-penetrometer.
# =============================================================================
# Measurement values ATI-penetrometer (same as above)
ati_penetrometer = np.asarray([19.86, 48.58, 7.83, 1.6])

# Measurement series light scattering detector (new version)
scatter1_new = np.asarray([23.9, 52.9, 4.8, 0.1])
scatter2_new = np.asarray([20.2, 32.1, 8.4, 0.4])
scatter3_new = np.asarray([15.1, 61.2, 5.2, 0.1])
scatter4_new = np.asarray([26, 77.1, 7.2, 0.8])
scatter5_new = np.asarray([17.6, 82.7, 6.9, 0.1])
scatter6_new = np.asarray([19.9, 79.9, 5.4, 0.1])

# Mean values and standard deviation of the scatter method
means_scatter_new = np.mean([scatter1_new, scatter2_new, scatter3_new,
                             scatter4_new, scatter5_new, scatter6_new], axis=0)
std_scatter_new = np.std([scatter1_new, scatter2_new, scatter3_new,
                         scatter4_new, scatter5_new, scatter6_new],
                         axis=0, ddof=1)
# Correlation coefficient
r_scatter_new = np.corrcoef(ati_penetrometer, means_scatter_new)

# Plot measurement results
plt.figure(4)
for i in range(4):
    plt.errorbar(ati_penetrometer[i], means_scatter_new[i], std_scatter_new[i],
                 marker=marl_er[i], capsize=3, elinewidth=1, label=mask[i],
                 linestyle='None')
    plt.plot([0, 70], [0, 70], 'k:', linewidth=1)

plt.xlabel('penetration in % certified penetrometer')
plt.ylabel('penetration in % scatter method')
plt.legend()
plt.grid(True)
plt.text(60.5, 0.5, 'r = %.3f' % round(r_scatter_new[0, 1], 3), fontsize=10)
plt.tight_layout()

# =============================================================================
# 
# =============================================================================
# Resistance masurement values ATI-penetrometer
ati_resistance = np.asanyarray([52.5, 12.7, 22.8])
# Resistance measurement new scatter method
resistance_scatter1 = np.asarray([913.3, 1143.6, 854.6])
resistance_scatter2 = np.asarray([952.6, 644.4, 919.6])
resistance_scatter3 = np.asarray([864.7, 953.6, 890.1])
resistance_scatter4 = np.asarray([1086.2, 859.7, 767.8])
resistance_scatter5 = np.asarray([979, 998.3, 746.8])
resistance_scatter6 = np.asarray([902.6, 915.1, 814.3])

# Mean values and standard deviation of the resistance measurement with the
# scatter method.
means_resistance = np.mean([resistance_scatter1, resistance_scatter2,
                           resistance_scatter3, resistance_scatter4,
                           resistance_scatter5, resistance_scatter6], axis=0)
std_resistance = np.std([resistance_scatter1, resistance_scatter2,
                         resistance_scatter3, resistance_scatter4,
                         resistance_scatter5, resistance_scatter6], axis=0,
                        ddof=1)
# Correlation coefficient
r_resistance = np.corrcoef(ati_resistance, means_resistance)

# Plot measurement results
plt.figure(5)
for i in range(3):
    plt.errorbar(ati_resistance[i], means_resistance[i], std_resistance[i],
                 marker=marl_er[i], capsize=3, elinewidth=1, label=mask[i],
                 linestyle='None')
    plt.plot([0, 70], [0, 70], 'k:', linewidth=1)

plt.xlabel('penetration in % certified penetrometer')
plt.ylabel('penetration in % scatter method')
plt.legend()
plt.grid(True)
plt.text(60.5, 0.5, 'r = %.3f' % round(r_resistance[0, 1], 3), fontsize=10)
plt.tight_layout()
