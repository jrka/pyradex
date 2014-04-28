import numpy as np
import pyradex

def grid_wrapper(molecule,
                 temperatures=[],
                 densities=[],
                 columns=[],
                 h2columns=[],
                 abundances=[],
                 transition_indices=[],
                 orthopararatios=[],
                 observable_parameters=['tex','source_line_surfbrightness','tau'],
                 ):


    ntemp = len(temperatures)
    ndens = len(densities)
    coltype = 'h2' if h2columns else 'mol'
    columns = columns or h2columns
    ncols = len(columns) or len(h2columns)
    nabund = len(abundances)
    nopr = len(orthopararatios)

    grids = {tid:
             {par: np.empty([ndens,ntemp,ncols,nabund,nopr])
              for par in observable_parameters}
             for tid in transition_indices}

    # Just a quick first run to get things initialized
    if coltype == 'mol':
        R = pyradex.Radex(species=molecule, column=columns[0], abundance=abundances[0])
    else:
        R = pyradex.Radex(species=molecule, h2column=h2columns[0], abundance=abundances[0])
    R.run_radex()

    # get the table so we can look at the frequency grid
    # table = R.get_table()

    # Target frequencies:
    # frequencies = table[np.array(transition_indices)]

    parameters_iterator = itertools.product(orthopararatios, columns, abundances, temperatures, densities)

    for opr,col,abund,tem,dens in parameters_iterator:
        fortho = opr/(1+opr)
        R.temperature = tem
        R.density = {'oH2':dd*fortho,'pH2':dd*(1-fortho)}
        if coltype == 'mol':
            R.column = col
        else:
            R.h2column = col
        R.abundance = abund # reset column to the appropriate value
        R.run_radex(reuse_last=False, reload_molfile=True)

        for tid in transition_indices:
            for par in observable_parameters:
                val = getattr(R, par)[tid]
                if hasattr(val,'value'):
                    val = val.value
                grids[tid][par] = val

    return grids