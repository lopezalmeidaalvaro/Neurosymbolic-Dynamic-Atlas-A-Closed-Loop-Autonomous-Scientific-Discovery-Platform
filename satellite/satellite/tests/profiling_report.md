# HPC Performance Profiling Report — CAD Importer Vectorization

This report presents a direct computational profiling comparison between the original $O(N^2)$ loop-based derivative solver and the newly vectorized NumPy matrix solver.

---

## 1. Top 15 Function Calls: Loop-Based Version
```text
         1385 function calls in 9.166 seconds

   Ordered by: cumulative time
   List reduced from 95 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    9.166    9.166 C:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\satellite\thermal\cad_thermal_importer.py:301(simulate_3d_thermal)
        1    0.000    0.000    9.166    9.166 C:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\satellite\thermal\cad_thermal_importer.py:253(simulate_3d_thermal_loop)
        1    0.000    0.000    9.132    9.132 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\ivp.py:159(solve_ivp)
       86    0.000    0.000    9.123    0.106 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:152(fun)
       86    0.000    0.000    9.123    0.106 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:22(fun_wrapped)
       86    9.122    0.106    9.122    0.106 C:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\satellite\thermal\cad_thermal_importer.py:268(dTemp_dt_loop)
       13    0.000    0.000    8.904    0.685 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:175(step)
       13    0.001    0.000    8.904    0.685 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:111(_step_impl)
       14    0.004    0.000    8.903    0.636 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:14(rk_step)
        1    0.000    0.000    0.225    0.225 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:85(__init__)
        1    0.000    0.000    0.119    0.119 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\common.py:68(select_initial_step)
       18    0.034    0.002    0.034    0.002 {built-in method numpy.array}
       13    0.000    0.000    0.001    0.000 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:251(__call__)
       13    0.001    0.000    0.001    0.000 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:560(_call_impl)
       14    0.000    0.000    0.001    0.000 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:108(_estimate_error_norm)



```

---

## 2. Top 15 Function Calls: Vectorized Version
```text
         3066 function calls (3052 primitive calls) in 0.056 seconds

   Ordered by: cumulative time
   List reduced from 356 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.056    0.056 C:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\satellite\thermal\cad_thermal_importer.py:301(simulate_3d_thermal)
       19    0.035    0.002    0.035    0.002 {built-in method numpy.array}
        1    0.000    0.000    0.018    0.018 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\ivp.py:159(solve_ivp)
       13    0.000    0.000    0.015    0.001 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:175(step)
       13    0.000    0.000    0.015    0.001 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:111(_step_impl)
       14    0.001    0.000    0.014    0.001 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\rk.py:14(rk_step)
       86    0.000    0.000    0.014    0.000 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:152(fun)
       86    0.000    0.000    0.014    0.000 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\scipy\integrate\_ivp\base.py:22(fun_wrapped)
       86    0.004    0.000    0.013    0.000 C:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\satellite\thermal\cad_thermal_importer.py:322(dTemp_dt)
      116    0.010    0.000    0.010    0.000 {method 'dot' of 'numpy.ndarray' objects}
        1    0.000    0.000    0.002    0.002 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\pandas\core\generic.py:3795(to_csv)
        1    0.000    0.000    0.002    0.002 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\pandas\io\formats\format.py:976(to_csv)
        1    0.000    0.000    0.001    0.001 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\pandas\io\formats\csvs.py:246(save)
       67    0.000    0.000    0.001    0.000 C:\Users\Alvaro\AppData\Local\Programs\Python\Python312\Lib\site-packages\numpy\core\fromnumeric.py:71(_wrapreduction)
       68    0.001    0.000    0.001    0.000 {method 'reduce' of 'numpy.ufunc' objects}



```

---

## 3. Mathematical Optimization & BLAS Advantages
- **Loop-Based Bottleneck**: Inside `dTemp_dt`, the pure Python interpreter executes nested `for i in range(1000):` and `for j in range(1000):` loops, running **1,000,000 checks and additions** per derivative step. Under Python's dynamic type checking, this locks the CPU execution thread.
- **Vectorized NumPy Acceleration**: By representing node conductances as a symmetric matrix $K$ and temperatures as a flat vector $\mathbf{y}$, we compute conduction via a single optimized matrix-vector dot product:
  
  $$\mathbf{Q}_{\text{cond}} = K \mathbf{y} - \mathbf{y} \odot \text{row\_sums}(K)$$
  
  Precomputing row sums results in a single BLAS-level dot product per step, written in compiled C. This reduces operations to a highly efficient memory-aligned sweep.
