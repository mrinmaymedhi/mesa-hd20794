import os

# Updated parameters
# Updated parameters
masses = [0.78, 0.79, 0.80]  # Added 0.9, 1.0
alphas = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]  # Added 1.3, 1.4
meshes = [0.0, 1.0, 2.0]  # Changed 0.0 to 0.1
initial_zs = [0.005, 0.0045]
atm_tables = ['photosphere','tau_100']  # Total 6*6*2*2 = 144 models


# Base inlist template
inlist_template = """
&star_job
   ! Job controls.
   create_pre_main_sequence_model = .true.
   !create_pre_main_sequence_model = .false.
   !set_uniform_initial_composition = .true.
   !initial_zfracs = 3
   
   ! Save model 
   !save_model_when_terminate = .true.
   !save_model_filename = 'ms_0.78_1.8.mod'
   
   ! Load model
   !load_saved_model = .true.
   !load_model_filename = 'zams_0.78.mod'
   
   pgstar_flag = .false.

   ! We need a larger nuclear network to include Silicon.
   ! The 'co_burn.net' and 'approx21.net' are good options.
   ! 'approx21.net' includes elements up to silicon.
   change_initial_net = .true.
   new_net_name = 'pp_cno_extras_ne22_pcl.net' # Medhi et al. (2023)

   ! Optional: For custom weak rates if defaults are insufficient
   use_suzuki_weak_rates = .true.  ! For A=17-28 weak rates, if relevant
   use_special_weak_rates = .false.  ! If needing fully custom fully handling

/ ! end of star_job namelist

&eos
   ! Equation of State module. Using default settings.
/ ! end of eos namelist

&kap
   ! Opacity module controls.
   use_Type2_opacities = .true.
   Zbase = {initial_z}

/ ! end of kap namelist

&controls
   ! Physics, evolution, and time stepping controls.

   ! Starting specifications.
   initial_mass = {mass}
   !initial_z = {initial_z}
   !initial_y = -1.0

   initial_z = {initial_z}
   initial_y = -1

   ! Stopping for star simulation
   !Teff_lower_limit = 5322
   !Teff_upper_limit = 5422
   !log_g_lower_limit = 4.4
   !log_g_upper_limit = 4.6

   history_interval = 1

   ! Stopping criteria for ZAMS: when core H starts burning (center_h1 slightly depleted)
   !xa_central_lower_limit_species(1) = 'h1'
   !xa_central_lower_limit(1) = 0.74  ! Adjust if initial X_H is different; stop just after burning onset
   !stop_near_zams = .true.

   ! Stopping criteria.
   max_age = 1d10
   !log_g_upper_limit = 4.60
   !xa_central_lower_limit_species(1) = 'he4'
   !xa_central_lower_limit(1) = 1d-6

   ! Physics controls.
   energy_eqn_option = 'dedt'
   use_gold_tolerances = .true.
   mixing_length_alpha = {alpha}
   mesh_delta_coeff = {mesh}

   atm_option = 'table'  ! Use table-based atmosphere
   atm_table = '{atm_table}'  ! Use photosphere tables (or 'atmos' for ATLAS9)

   ! Additional control for predictive mixing to be thorough.
   !predictive_mix(1) = .true.
   !predictive_zone_type(1) = 'any'  ! This is also needed
   !predictive_zone_loc(1) = 'any'   ! Add this line with a valid option.
/ ! end of controls namelist
"""

# Current directory
current_dir = os.getcwd()

# Generate and run all models by overwriting inlist_project
# Generate and run all models by overwriting inlist_project
model_count = 0
for mass in masses:
    for alpha in alphas:
        for mesh in meshes:
            for initial_z in initial_zs:
                for atm_table in atm_tables:
                    print(f"Running model {model_count:02d}: M={mass}, alpha={alpha}, mesh={mesh}, z={initial_z}, atm={atm_table}")
                    with open('inlist_project', 'w') as f:
                        f.write(inlist_template.format(mass=mass, alpha=alpha, mesh=mesh, initial_z=initial_z ,atm_table=atm_table))
                    os.system('./clean') 
                    os.system('./mk')  # Recompile if needed
                    os.system('./rn')  # Run the model
                    # Rename the LOGS folder to avoid overwrite
                    if os.path.exists('LOGS'):
                        new_logs_name = f'LOGS_{mass}M_MLT_{alpha}_mesh_{mesh}_atm_{atm_table}_z_{initial_z}'
                        if os.path.exists(new_logs_name):
                            os.rmdir(new_logs_name)  # Remove if exists (empty)
                        os.rename('LOGS', new_logs_name)
                    model_count += 1

print(f"Completed {model_count} models.")