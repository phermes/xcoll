import numpy as np

import matplotlib.pyplot as plt

import xtrack as xt
import xpart as xp
import xcoll as xc

import sixtracktools as st


# --------------------------------------------------------
# -------------------- Initialisation --------------------
# --------------------------------------------------------

# Import Run III lattice
print("Loading line from SixTrack.. ")
line = xt.Line.from_sixinput(st.SixInput('./RunIII_B1'))

# Attach reference particle (a proton at 6.8 TeV)
line.particle_ref = xp.Particles(mass0 = xp.PROTON_MASS_EV, p0c=6.8e12)

# Switch on RF (needed to twiss)
line['acsca.d5l4.b1'].voltage = 16e6
line['acsca.d5l4.b1'].frequency = 1e6

# Initialise collmanager
coll_manager = xc.CollimatorManager(
    line=line,
    colldb=xc.load_SixTrack_colldb('RunIII_B1/CollDB-RunIII_B1.dat', emitx=3.5e-6, emity=3.5e-6)
    )

# Install collimators in line as black absorbers
print("Installing black absorbers.. ")
coll_manager.install_black_absorbers(verbose=True)

# Build the tracker
tracker = line.build_tracker()

# Set the collimator openings based on the colldb,
# or manually override with the option gaps={collname: gap}
coll_manager.set_openings()



# --------------------------------------------------------
# ------------------ Tracking (test 1) -------------------
# --------------------------------------------------------
#
# As a first test, we just track 5 turns.
# We expect to see the transversal profile generated by
# the three primaries opened at 5 sigma.


# Create initial particles
n_sigmas = 10
n_part = 50000
x_norm = np.random.uniform(-n_sigmas, n_sigmas, n_part)
y_norm = np.random.uniform(-n_sigmas, n_sigmas, n_part)
part = xp.build_particles(tracker=tracker, x_norm=x_norm, y_norm=y_norm,
                          scale_with_transverse_norm_emitt=(3.5e-6, 3.5e-6),
                          at_element='tcp.d6l7.b1',
                          match_at_s=coll_manager.s_start_active['tcp.d6l7.b1']
                         )

# Track
print("Tracking first test.. ")
tracker.track(part, num_turns=5)

# The survival flags are sorted as surviving particles first,
# hence we need to 'unsort' them using their IDs
surv = part.state.copy()
surv[part.particle_id] = part.state

# Plot the surviving particles as green
plt.figure(1,figsize=(12,12))
plt.plot(x_norm, y_norm, '.', color='red')
plt.plot(x_norm[surv>0], y_norm[surv>0], '.', color='green')
plt.axis('equal')
plt.axis([n_sigmas, -n_sigmas, -n_sigmas, n_sigmas])
plt.show()


# --------------------------------------------------------
# ------------------ Tracking (test 2) -------------------
# --------------------------------------------------------
#
# As a second test, we remove all collimator openings
# (which is done by setting them to 1 meter) except the
# horizontal primary. We give the latter an asymmetric
# opening, and an angle of 15 degrees.
# This is done to check our coordinate implementations.
# We only track one turn, because otherwise betatron
# oscillations would make the cut profile symmetric anyway.

coll_manager.colldb.angle = {'tcp.c6l7.b1': 15}
coll_manager.set_openings({'tcp.c6l7.b1': [4,7]}, full_open=True)

# Create initial particles
part = xp.build_particles(tracker=tracker, x_norm=x_norm, y_norm=y_norm,
                          scale_with_transverse_norm_emitt=(3.5e-6, 3.5e-6),
                          at_element='tcp.c6l7.b1',
                          match_at_s=coll_manager.s_start_active['tcp.c6l7.b1']
                         )

# Track
print("Tracking second test.. ")
tracker.track(part, num_turns=1)

# The survival flags are sorted as surviving particles first,
# hence we need to 'unsort' them using their IDs
surv = part.state.copy()
surv[part.particle_id] = part.state

# Plot the surviving particles as green
plt.figure(1,figsize=(12,12))
plt.plot(x_norm, y_norm, '.', color='red')
plt.plot(x_norm[surv>0], y_norm[surv>0], '.', color='green')
plt.axis('equal')
plt.axis([n_sigmas, -n_sigmas, -n_sigmas, n_sigmas])
plt.show()
