# High Performance Python by Micha Gorelick & Ian Ozsvald

---

## 1. Understanding Performant Python
## 2. Profiling to Find Bottlenecks
## 3. List and Tuples
## 4. Dictionaries and Sets
## 5. Iterators and Generators
## 6. Matrix and Vector Computation
## 7. Compiling to C
## 8. Asynchronous I/O
## 9. The multiprocessing Module
## 10. Clusters and Job Queues
## 11. Using Less RAM
## 12. Lessons from the Field

---

# 1. Understanding Performant Python

## The Fundamental Computer System

The underlying components that make up a computer can be simplified into three basic parts: ***the computing units***, ***the memory units***, and ***the connections between them***. In addition, each of these units has different properties that we can use to understand them. The computational units has the property of how many computations it can do per second, the memory unit has the properties of how much data it can hold and how fast we can read from and write to it, and finally, the connections have the property of how fast they can move data form one place to another.

Using these building blocks, we can talk about a standard workstation at multiple levels of sophistication. For example, the standard workstation can be thought of as having a central processing unit (CPU) as the computational unit, connected to both the random access memory (RAM) and the hard drive as two separate memory units ( each having different capacities and read/write speeds), and finally a bus that provides the connections between all of these parts. However, we can also go into more detail and see that the CPU itself has several memory units in it: the L1, L2, and sometimes even the L3 and L4 cache, which have small capactiies but very fast speeds ( from several kilobytes to a dozen megabytes ). Furthermore, new computer architectures generallly come with new configurations (for example, Intel's SkyLake CPUs replaced the frontside bus with the Intel Ultra Path Interconnect and restructured many connections). Finally, in both of these approximations of a workstation we have neglected the network connection, which is effectively a very slow connection to potetionally many other computing and memory units.

### Computing Units

The *computing unit* of a computer is the centerpiece of its usefulness - it provides the ability to transofmr any bits it receives into other bits or to change the state of hte vcurrent process. CPUs are the most commonly used for computing unit; however, graphics processing units (GPUs) are gaining popularity as auxiliary computing units. They were orignally used to speed up computer graphics but are becoming more applicable for numerical applications and are useful thanks to their intrinsically parallel nature, which allows many calculations to happen simultaneously. Regarldess of its type, **a computing unit takes a series of bits** (for example, bits representing numbers) **and outputs another set of bits** (for example, bits representing the sum of those numbers). In addition to the basic arithmetic operations on integers and real numbers and bitwise operations on binary numbers, some computing units also provide very specialized operations, such as the "fused multiply add" operation, which takes in threee numbers A, B, and C, and returns the value ```A*B + C```.

**The main properties** of interest in a comuting unit are **the number of operations it can do in one cycle** and **the number of cycles it can do in one second**. The first value is measured by its **insturctions per cycle (IPC)**, whithe the latter is measured by its **clock speed**. These two measures are always competing with each other when new computing units are being made. For example, the Intel Core series has a very high IPC but a lower clock speed, while the Pentium 4 chip has the reverse. GPUs, on the other hand, hav ea very high IPC and clock speed, but they suffer from other problems like the slow communications.

Furthermore, although increaseing clock speed almost immeidately speeds upa ll programs running on that computational unit (because they ar eable to do more calculations per second), **having a higher IPC can also drastically affect computing by changing the level of vectorization that is possible.**
**Vectorization occurs when a CPU is provided with multiple pieces of data at a time and is able to operate on all of them at once. This sort of CPU instruction is known as single instruction, multipel data (SIMD).**

In general, computing units have advanced quite slowly over the past decade. Clock speeds and IPC have both been stagnant because of the physical limitations of making transistors smaller and smlaler. As a reuslt, **chip manufacturers have been relying on other methods to gain more speed**, including **simultaneous multithreaiding** (where multiple threads can run at once), more clever **out-of-order execution**, and **multicore architectures**.

![Clock Speed Of CPUs Over Time](ScreenshotsForNotes/Chapter1/ClockSpeedOfCPUsOverTime.jpg)

**Hyperthreading** presents a virutal second CPU to the host operationg system (OS), and clever hardware logic tries to interleave two threads of insturctions into the exeuction units on a single CPU. When successful, gains of up to 30% over a single thread can be achieved. Typically, this works well when the units of work across both threads use different types of executin units - for example, one performs floating-point operations and the other performs integer operations.

**Out-of-order execution** enables a compiler to spot that some parts of a linear program sequence do not depend on the reuslts of a previous piece of work, and therefore that both pieces of work could occur in any order or at the same time. As long as sequential results are presented at the right time, the program continues to execute correctly, even though pieces of work are computed out of their programmed order. This enables some instructions to execute when other might be blocked (e.g., waiting for a memory access), allowing greater overall utilization of the avaialble resources.

**Multicore architectures** include multiple CPUs withing the same unit, whcih increases the total capability without running into barriers to making each individual unit faster. This is why it is currently hard to find any machine with fewer that wo cores - in this case, the compute rhas two physical computing units that are connected to each other. While this increases the total number of operations that *can* be done per second, it can make writing code more difficult!

Simply adding more cores to a CPU does not always speed up a program's exeuction time. This is because of something known as *Amdahl's law*:

> *Amdahl's law*: if a program designed to run on multiple cores has some subroutines that must run on one core, this will be the limitation for the maximum speedup that can be achieved by allocating more cores.

For example, if we had a survey we wanted one hundred people to fill out, and that survey took 1 minute to complete, we could complete thsi task in 100 minutes if we had one person asking the questions (i..e, this person goes to participatn 1, ask s the questions, wait s fo rthe responses, and then moves to participant 2). This method of having one person asking the questions and waiting for responses is similar to a serial prcoess. In serial processes, we have operations being satisfied one at a time, each one waiting for the previous operations to complete.

However, we could perfomr the survey in parallel if we had two people asking the questions, which would let us finish the process in only 50 minutes. This can be done because each individual person asking the questions does not need to know anything about the other person asking questions. As a result, the task can easily be split up without having any dependency between the question askers.

Adding more people asking the questions will give us more speedups, until we have one hundred people asking questions. At this pint, the process would take 1 minutes and would b elimited simply by the time it takes a participant to answer questions. Adding more epopel asking questions will not result in any further speedups ,because these extra people will have no tasks to perform - all the participants are already being asked questions! At this point, the only way to reduce the overall time to run the survey is to **reduce the amount of time it takes for an individual survey, the serial portion of the problem, to complete.** Similarly, with CPUs, we can add more cores that can perform various chunks of the computation as necessaru until we reach a piont where the bottleneck is the time it takes for a specific core to fnish its task. **In other words, the bottleneck in any parallel calculation is always the smaller serial tasks that are being spread out.**

Furthermore, a major hurdle with utilizing multiple cores in Python is Python's use of a *global interpreter lock (GIL)*. The GIL makes sures that a Python process can run only one insturction at a time, regardless of the number of cores it is currently using. This means that even though some Python code has access to multiple cores at a time, only one core is running a Python instruction at any given time. Using the previous example of a survey, this would mean that even if we had 10 question askers, only one person could ask a question and listen to a response at a time. This effectively removes any sort of benefit from having multiple question askers! While this may seem like quite a hurdle, especially if hte current tnred in computing is to have multiple computing units rather than having afster ones, **this problem can be avoided by using other standard library tools, like ```multiprocessing```, technologies like ```numpy``` or ```numexpr```, ```Cython```, or distributed models of computing.**

### Memory Units

**Memory units in computers are used to store bits.** These could be bits representing variables in your program or bits representing the pixels of an image. Thus, the abstraction of a memory units applies to the registers in your motherboard as well as your RAM and hard drive. **The one major difference** between all of these types of memory units **is the speed at which they can read/write data.** To make things more complicated, the read/write speed is heavily dependent on the way that data is being read.

For example, most memory units perform much better when they read one large cunks of data as opposed to many small chunks (this is referred to as *sequential read* versus *random data*). If the data in these memory units is though of as pages in a large book, this means that most memory units have better read/write speeds when going through the book page by page rather tha constantly flipping from one random page to another while this fact is gneerally true across all memory units, the amount that this affects each type is drastically different.

In addition to the read/write speeds, memory units also have **latency**, which can be characterized as **the time it takes the device to find the data that is being used**. For a spinning hard drive, this latenc ycan be high because the disk needs to physically spin up to speed and the read head must move to the right position. On the other hand, for RAM, this latency can be quite small because everything is solid state. Here is a description of hte various memory untis htat are commonly found inside a standard workstation, on order of read/write speeds:

* *Spinning hard drive*
    * Long-term storage that persists even when the computer is shut down. Generally has slow read/write speeds because the disk must be physically spun and moved. Degraded performance iwth random access patterns but very large capacity (10 terabyte range).
* *Solid-state hard drive*
    * Similar to a spinning hard drive, with faster read/write speeds but smaller capacity (1 terabyte range).
* *RAM*
    * Used to store application code and data (such as any variables being used). Has fast read/write cahracteristics and performs well with random access paterns, but is generally limited in capacity (64 gigabyte range).
* *L1/L2 cache*
    * Exteremly fast read/write speeds. Data going to the CPU *must go* through here. Very small capacity (megabytes range).

The following figure gives a graphic representaiton of the differneces between these types of memoyr units by looking at the characteristics of currently available consumer hardware:

![Characteristic Values For Differnet Types Of Memory Units](ScreenshotsForNotes/Chapter1/CharacteristicValuesForDifferentTypesOfMemoryUnits.PNG)

A clearly visible trend is that read/write speeds and capacity are inversely proportional - ***as we try to increase speed, capacity gets reduced***. Because of this , many systems implemented a tiered approach to memory: data starts in its full state in the hard drive, part of it moves to RAM, and then a much smaller subset moves to the L1/L2 cache. This method of tiering enables programs to keep memory in different places depending on access speed requirements. **When trying to optimize the memory patterns of a program, we are simply optimizing which data is placed where, how it is laid out (in order to increase the number of sequential reads), and how mnay times it is moved among the variosu locations.** In addition, methods such as asynchronous I/O and preemptive caching provide ways to make sure that data is always where it needs to be without having to waste computing time - most of these processes can happen independently, while other calculations are being performed!

### Communications Layer

**Many modes of communication exist, but all are variants on a thing called a bus.**

The **frontside bus**, for example, is the **connection between the RAM and the L1/L2 cache.** It mvoes data that is ready to be transformed by the processor into the staging ground to get ready for calculation, nad it moves finished calculations outs. There are other buses, too, such as **the external bus** that acts as the **main route from hardware devices to the CPU and system memory.** The external bus is generally slower than the frontside bus.

In fact, many of the benefits of the L1/L2 cache are attributable ot hte faster bus. BEing able to queue up data necessary for computation in large chunks on a low bus ( from RAM to cache) and then having it available at very fast speeds from the cache lines (from cache to CPU) enable sthe CPU to do more calculations without waiting such a long time.

Similarly, many of the drawbacks of using a GPU come from the bus it is connected on: **since the GPU is generally a peripheral device, it communicates through the PCI bus, which is much slower than the frontside bus.** As a reuslt, **geting data into and out of the GPU can be qutie a taxing operation.** The advent of heterogeneous computing, or computing blocks that have both a CPU and a GPU on the frontside bus, aims at reducing the data transfers cost and making GPU comptuing more of an avaialable option, even when a lot of data must be transferred.

In addition to the communication blocks withing the computer, the network can be though of as yet another communication block. This block, though, is much more pliable than the ones discucseed previously; a network device can be connected to a memory device, such as a network attached storage (NAS) device or another computing block, as in a computing node in a cluster. However, networkg communications are generally much slower than the other types of communications mentioned previously. While the frontside bus can transfer doznes of gigabits per second, the network is limited to the order of several dozen megabits.

It is clear, then, that **the main propery of a bus is its speed: how mcuh data it can move in a given amount of time.** This property is given by combining two quantities: **how mcuh data can be moved in one transfers (bus width)** and **how many transfers the bus can do per second (bus frequency).** It is important to note that the **data moved in one transfer is always sequential: a chunk of data is read off of the memory and moved th a different place.** Thus, the speed of a bus is borken into these two quantities because individually they can affect different aspects of computation: **a lareg bus width can help vectorized code (or any code that sequentially reads through memory) by making it possible to move all the relevant data in one tranfer**, while, on the other hand, **having a small bus with but a very high frequency of transfers can help code that must do many reads from random parts of memory.** Interestingly, one of the ways that these properties are changed by computer designers is by the physical layout of the motherboard: when chips are placed close to another one, the lenght of the phhysical wires joining them is smaller, which can allow for faster transfer sppeds. In addition, the number of wires itself dictates the widht of the bus (giving real physical meaning to the term).

Since interface can be ve the right performance for a specific application, it is no surprise that there are hundred of types. The following figure shows the bitrates for a sampling of common interfaces. Note that htis doesn't speak at all about the latency of the connections, which dictates how long it teakes for a data request to be responeded to (although latency is very computer-dependent, some basic limitations are inherent to the interfaces being used).

![Connection Speeds Of Various Common Interfaces](ScreenshotsForNotes/Chapter1/ConnectionSpeedsOfVariousCommonInterfaces.PNG)

## How to be a highly performant programmer

Writing high performance code is only one part of being highly performant with successful projects over the longer term. Overall team velocity is far more important than speedups and complicated solutions. Several factors are key to this - good structure, documentation, debuggability, and shared standards.

Let's say you create a prototype. You didn't test it thoroughly, and it didn't get reviewed by yourr team. It does seem to be "good enough", and it gets pushed to production. Since it was never written in a structured way, it lacks tests and is undocumented. All of a sudden there's an inertia-causing piece of code for someone else to support, and often management can't quantify the cost to the team.

As this solution is hard to maintian, it tends to stay unloved - it never gets restructured, it doesn't get the tests that'd help the team refactor it, and nobody else like to touch it, so it falls to one developer to keep it running. This can cause an awful bottleneck at times of stress and raises a significant risk: what would happen if that developer left the project?

Typically, this development style occurs when the management team doesn't understand the ongioing inertia that's cause by hard-to-maintain code. Demonstrating that in the longer-term tests and documentation can hlep a team stay highly productive and can help convince managers to allocate time to "cleaning up" this prototype code.

In a research environment, it is commong ot create many Jupyter Notebooks using poor coding practices whiel tierating through ideas and different datasets. The intention is alwyas to "write it up properly" at a later stage, but that later stage never occurs. In the ends, a working result is obtained ,but the infrastrucutre to reproduce it, test it, and trust the result is missing. Once again the ris kfasctors are high, and the truste in the reuslt will be low.

There's a general approach that will serve you well:

* *Make it work*
    * First you build a good-enough solution. It is very sensible to "build one to throw away" that acts as a prototype solution, enabling a better structure to be used for the second version. It is always sensible to do some up-front plnning before coding; otherwise, you'll come to reflect that "We saved an hou'rs thinking by coding all afternoon." In some fields this is better known as "Mesaure twice, cut once."
* *Make it right*
    * Next, you add a strong test suite backed by documentation and clear reproducibility insturctions so that another team member can take it on.
* *Make it fast*
    * Finally, we can focus on profiling and compiling or parallelization and using the existing test usite to confirm that hte new, faster solution still works as expected.

## Good Working Practices

***There are a few "must haves" - documentation, good structure, and testing are key.***

**Some project-level documentation** will help you stick to a clean structure. It'll also help you and your colleagues in the future. Nobody will thank you if you skip this part. Writing this up in a *READMDE* fil at the top level is a sensible starting point; it can always be expaneded into a ```docs/``` folder later if required.
Explain the purpose hf the project, what's in the folders, where the data comes from, which files are critical, and how to run it all, including how to run the tests.

**It is recommended to use Docker.** A top-level Dockerfile will explain to your future-self exactly which libraries you need from the operatin system to make this project run successfully. It also removes the difficulty of running this code on other machines or deploying it to a cloud environment.

**Add a ```tests/``` folder and add some unit tests.** Preferable is ```pytest``` as a modern test runner, as it builds on Python's built-in ```unittest``` module. Start with just a couple of tests and then build them up. Progress to using the ```coverage tool```, which will report how many lines of your code are actually covered by the tests - it'll help avoid nasty surprises.
If you're inheriting legacy code and it lacks test, a high-value activity is to add some tests up front. Some "integration tests" that check the overall flow of the project and confirm that with certain input data you get specific output results will help your sanity as you subsequently make modifications.

**Docstrings** in your code for each function, class and module will always help you. Aim to provide a useful description of what's achieved by the function, and where possible include a short example to demonstrate the expected output.

Whenver your code becomes too long - such as functions logner than one screen - be comforatble with refactoring the code to make it shorter. ***Shorted code is easier to test and easier to support.***

> When you're developing tests, think about following a test-driven development methodology. Whne you know exactly what ou need to develop and you have testable example s at hand - this method become very efficient.
>
> You write your tests, run them, watch them fail, and *then* add the funcitons and the necessary minimum logic to support the tests that you've written. When your tests all work, you're done. By figuring out the expected input and output of a function ahead of time, you'll find implementing the logic of the function relatively straight forward.
>
> If you can't define yuor ests ahead of time, it naturally riase sthe question, do you real understand what your function needs to do? If not, can you write it correctly in an efficient manner?
>
> ***This method doesn't work so well if you're in a creative process and researching data that you don't yet understand well.***

**Always use source control** - you'll only thank yourself when you overwrite something critical at an inconvenient moment. Get used to committing frequently (daily, or even every 10 minutes) and pushing to your repository every day.

**Keep to the standard PEP8 coding standard.** Even better, adopt **```black```** (the opinionated code formatter) on a pre-commit source control hook so it just rewrite your code to the standard for you. Use **```flake8```** to lint your code to avoid mistakes.

**Creating environments that are isolated from the operatinog system will make your life easier.** You can use Anaconda or a combination between ```pipenv``` and Docker. Both are sensible solutions and are significanlty better than using the operating system's global Python environment!

**Remember that automation if your friend.** Doing less manual work means there's less chance of errors creeping in. Automated build systems, continuous integrationg with automated test suite runners, and automated deployment systems turn tedious and error-prone tasks into standard processes that anyone can run and support.

Finally, remmeber that ***readability is far mroe improtant than being clever.*** Short sinppets of complex and hard-to-read code will be hard for you and your colleagues to maintain, so people will be scared of touching this code. Instead, write a longer, easier-to-read function and back it with useful documentation showing that it'll returng, and complement this with tests to confirm that it *does* work as you expect.

# 2. Profiling to Find Bottlenecks

## What is profiling

***Profiling lets us find bottlenecks so we can do the least amount of work to get the biggest practical performance gain.***

Any measurable resource can be profiled, not just the CPU. You can apply profiling techniques to network bandwidth and disk I/O as well.

If a program is running slowly because it's using too much RAM then you should identify the part of the program that does that and modify it. You can also skip profiling at this point and change whatever it is that you *believe* is wrong with the code. The problem with using your intuition is that you'll often end up fixing the wrong thing. **Rather than using your intuition, it is far better to first profile, having defined a hypothesis, before making changes to the structure of your code.**

```-> >```

## Profiling efficiently

The first aim of profiling is to **test a representative system to identify what's slow** (or using too much RAM, or causing too much disk I/O or network I/O). Profiling typically adds an overhead (10x to 100x slowdowns can be typical), and you still want your code to be used in as similar to a real-world situation as possible. Extract a test case and isolate the piece of the system that you need to test. Preferably, it'll have been written to be in its own set of modules already.

Whatever approach you take to profiling your code, you must remember to have adequate unit test coverage in your code. Unit tests help you to avoid silly mistakes and to keep your results reproducible. Avoid them at your peril.

*Always* profile your code before compiling or rewriting your algorithms. You need evidence to determine the most efficient ways to make your code run faster.

## Introducing the Julia Set

The Julia set is a fractal sequence that generates a complex output image.

We will analyze a block of code that produces both a false grayscale plot and a pure grayscale variant of the Julia set, at the complex point ```c=-0.62772 -0.42193j```. A Julia set is produced by calculating each pixel in isolation.

The following figure is a Julia set plot with a false gray scale to highlight detail:

![Julia set plot with a false gray scale to highlight detail](ScreenshotsForNotes/Chapter2/JuliaSetPlotWithAFalseGrayScaleToHighlightDetail.PNG)

If we chose a different ```c```, we'd get a different image. The location we have chosen has regions that are quick to calculate and other that are slow to calculate; this is useful for our analysis.

The problem is interesting because we calculate each pixel by applying a loop that could be applied an indeterminate number of times. On each iteration we test to see if this coordinate's value escapes toward infinity, or if it seems t be held by an attractor. Coordinates that cause few iterations are colored darkly in the figure above, and those that cause a high number of iterations are colored white. White regions are more complex to calculate and so take longer to generate.

We define a set of ```z``` coordinates that we'll test. The function that we calculate squares the complex number z and adds c: ```f(z) = z^2 + c```.

We iterate on this function while testing to see if the escape condition holds using ```abs```. If the escape function is ```False```, we break out of the loop adn record the number of iterations we performed at this coordinate. If the escape function is never ```False```, we stop after ```maxiter``` iterations. We will later turn this ```z```'s result into a colored pixel representing this complex location.

In pseudocode, it might look like this:

```
for z in coordinates:
  for iteration in range(maxiter):  # limited iterations per point
    if abs(z) < 2.0:  # has the escape condition been broken?
      z = z*z + c
    else:
      break
  
  # store the iteration count for each z and draw later
```

To explain this function, let's try two coordinates.

We'll use the coordinate that we draw in the top-left corner of the plot at ```-1.8-1.8j```. We must test ```abs(z)``` < 2 before we can try to update rule:

```python
z = -1.8-1.8j
print(abs(z))

"""
Output:

z = -1.8-1.8j
print(abs(z))
"""
```

We can see that for the top-left coordinate, the ```abs(z)``` test will be ```False``` on the zeroth iteration as ```2.54 >= 2.0```, so we do not perform the update rule. The ```output``` value for this coordinate is ```0```.

Now let's jump to the center of the plot at ```z = 0 + 0j``` and try a few iterations:

```python
c = -0.62772-0.42193j
z = 0+0j
for n in range(9):
    z = z*z + c
    print(f"{n}: z={z:.5f}, abs(z)={abs(z):0.3f}, c={c:.5f}")

"""
Output:

0: z=-0.62772-0.42193j, abs(z)=0.756, c=-0.62772-0.42193j
1: z=-0.41171+0.10778j, abs(z)=0.426, c=-0.62772-0.42193j
2: z=-0.46983-0.51068j, abs(z)=0.694, c=-0.62772-0.42193j
3: z=-0.66777+0.05793j, abs(z)=0.670, c=-0.62772-0.42193j
4: z=-0.18516-0.49930j, abs(z)=0.533, c=-0.62772-0.42193j
5: z=-0.84274-0.23703j, abs(z)=0.875, c=-0.62772-0.42193j
6: z=0.02630-0.02242j, abs(z)=0.035, c=-0.62772-0.42193j
7: z=-0.62753-0.42311j, abs(z)=0.757, c=-0.62772-0.42193j
8: z=-0.41295+0.10910j, abs(z)=0.427, c=-0.62772-0.42193j
"""
```

We can see that each update to ```z``` for these first iterations leaves it with a value where ```abs(z) < 2``` is ```True```. For this coordinate we can iterate 300 times, and still the test will be ```True```. We cannot tell how many iterations we must perform before the condition becomes ```False```, and this may be an infinite sequence. The maximum iteration (```maxiter```) break clause will stop us from iteration potentially forever.

In the following figure, we see the first 50 iterations of the preceding sequence. For ```0+0j``` (the solid line with circle markers), the sequence appears to repeat every eighth iteration, but each sequence of seven calculations has a mnior deviation from the previous sequence - we can't tell if this point will iterate forever within the boundary condition, or for a long time, or maybe for just a few more iterations. The dashed ```cutoff``` line shows the boundary at +2:

![Two coordinate examples evolving for the Julia set](ScreenshotsForNotes/Chapter2/TwoCoordinateExamplesEvolvingForTheJuliaSet.PNG)

For ```-0.82+0j``` (the dashed line with diamond markers), we can see that after the ninth update, the absolute result has exceeded the +2 cutoff, so we stop updating this value.

## Calculating the Full Julia Set

At the start of our module we import the ```time``` module for our first profiling approach and define some coordainte constants.

```python
"""Julia set generator without optional PIL-based image drawing"""
import time

# area of complex space to investigate
x1, x2, y1, y2 = -1.8, 1.8, -1.8, 1.8
c_real, c_imag = -0.62772, -.42193
```

To generate the plot, we create two lists of input data. The first is ```zs``` (complex ```z``` coordinates), and the second is ```cs``` (a complex initial condition). Neither list varies, adn we could optimize ```cs``` to a single ```c``` value as a constant. The rationale for building two input lists is so that we have some reasonable-looking data to profile when we profile RAM  usage later in this chapter.

To build the ```zs``` and ```cs``` lists, we need to know the coordinates for each ```z```. In the following example, we build up these coordinate using ```xcoord``` and ```ycoord``` and a specified ```x_step``` and ```y_step```. The somewhat verbose nature of this setup is useful when porting the code to other tools (such as ```numpy```) and to other Python environments, as it helps to have everything *very* clearly defined for debugging:

```python
def calc_pure_python(desired_width, max_iterations):
  """Create a list of complex coordinates (zs) and complex parameters (cs), build Julia set"""
  x_step = (x2 - x1) / desired_width
  y_step = (y1 - y2) / desired_width

  x = []
  y = []

  ycoord = y2
  while ycoord > y1:
    y.append(ycoord)
    ycoord += y_step

  xcoord = x1
  while xcoord < x2:
    x.append(xcoord)
    xcoord += x_step

  # build a list of coordinates and the initial condition for each cell
  # Note that ur initial condition is a constant and could easily be removed,
  # we use it to simulate a real-world scenario with several inputs to our
  # function

  zs = []
  cs = []
  for ycoord in y:
    for xcoord in x:
      zs.append(complex(xcoord, ycoord))
      cs.append(complex(c_real, c_imag))

      print("Length of x:", len(x))
      print("Total elements:", len(zs))
      start_time = time.time()
      output = calculate_z_serial_purepython(max_iterations, zs, cs)
      end_time = time.time()
      secs = end_time - start_time
      print("{0} took {1} seconds".format(calculate_z_serial_purepython.__name__, secs))

      # This sum is expected for a 1000^2 grid with 300 iterations
      # It ensures that our code evolves exactly as we'd intended
      assert sum(output) == 33219980
```

Having built the ```zs``` and ```cs``` lists, we output some information about the size of hte lists and calculate the ```output``` list via ```calculate_z_serial_purepython```. Finally, we ```sum``` the contents of ```output``` and ```assert``` that it matches the expected output value.

As the code is deterministic, we can verify that the function works as we expect by summing all the calculated values. This is useful as a sanity check - when we make changes to numerical code, it is *very* sensible to check that we haven't broken the algorithms. Ideally, we could use unit tests and test more than one configuration of the problem.

Next, in the following example, we define the ```calculate_z_serial_purepython``` function, which expands on the algorithm we discussed earlier. Notably, we also define an ```output``` list at the start that has the same length as the input ```zs``` and ```cs``` lists:

```python
def calculate_z_serial_purepython(maxiter, zs, cs):
  """Calculate output list using Julia update rule"""
  output = [0] * len(zs)
  for i in range(len(zs)):
    n = 0
    z = zs[i]
    c = cs[i]

    while abs(z) < 2 and n < maxiter:
      z = z * z + c
      n += 1

    output[i] = n

  return output
```

Now we call the calculation routine in the next example. By wrapping it an a ```__main__``` check, we can safely import the module without starting the calculations for some of the profiling methods. Here, we're not showing the method used to plot the output:
    
```python
if __name__ == '__main__':
  # Calculate the Julia set using a pure Python solution with
  # reasonable defaults for a laptop
  calc_pure_python(desired_width=1000, max_iterations=300)

"""
Output:

Length of x: 1000
Total elements: 7172
calculate_z_serial_purepython took 0.015624761581420898 seconds
"""
```

In the false-grayscale plot, the high-contrast color changes gave us an idea of where the cost of the function was slow changing or fast changing. Here, in the following figure, we have a linear color map: black is quick to calculate, and white is expensive to calculate.

By showing two representations of the same data, we can see that lots of detail is lost in the linear mapping. Sometimes it can be useful to have various representations in mind when investigating the cost of a function:

![Julia plot example using a pure gray scale](ScreenshotsForNotes/Chapter2/JuliaPlotExampleUsingAPureGrayScale.PNG)

## Simple Approaches to Timing - print and a Decorator

You must observe the normal variation when you're timing your code, you might incorrectly attribute an improvement in your code to what is simply a random variation in execution time.

Your computer will be performing other tasks while running your code, such as accessing the network, disk, or RAM, and these factors can cause variations in the execution time of your program.

Using ```print``` statements is the simplest way to measure the execution time of a piece of code *inside* a function. It is a basic approach, but despite being quick and dirty, it can be very useful when you're first looking at a piece of code.

Using ```print``` statements is commonplace when debugging and profiling code. It quickly become unmanageable but is useful for short investigations. Try to tidy up the ```print``` statements when you're done with them, or they will clutter your ```stdout```.

A slightly cleaner approach is to use a *decorator*:

```python
from functools import wraps

def timefn(fn):
  @wraps(fn)
  def measure_time(*args, **kwargs):
    t1 = time.time()
    result = fn(*args, **kwargs)
    t2 = time.time()
    print(f"@timefn: {fn.__name__} took {t2 - t1} seconds")
    return result

  return measure_time


@timefn
def calc_pure_python(desired_width, max_iterations):
    ...
```

> The addition of profiling information will inevitably slow down your code - some profiling options are very informative and induce a heavy speed penalty. The trade-off between profiling detail and speed will be something you have to consider.

We can use the ```timeit``` module as another way to get a coarse measurement of the execution speed of our CPU-bound function.

> The ```timeit``` module temporarily disabled the garbage collector. This might impact the speed you'll see with real-world operations if the garbage collector would normally be invoked by your operations.

From the command line, you can run ```timeit``` as follows:

```bash
$ python -m timeit -n 5 -r 1 -s "import julia" \
  "julia1.calc_pure_python(desired_width=1000, max_iterations=300)"
```

```n``` is the number of loops and ```-r``` is the number of repetitions. The best result of all repetitions is given as the answer.

## Using the cProfile Module

```cProfile``` is a built-in profiling tool in the standard library. It hooks into the virtual machine in CPython to measure the time taken to run every function that it sees. This introduces a greater overhead, but you get correspondingly more information. Sometimes the additional information can lead to surprising insights into your code.

```cProfile``` is one of two profilers in the standard library, alongside ```profile.profile``` is the original and slower pure Python profiler; ```cPorfile``` ahs teh same interface as ```profile``` and is written in ```C``` for a lower overhead.

***A good practice when profiling is to generate a hypothesis about the speed of parts of your code before you profile it. Forming a hypothesis ahead of time means you can measure how wrong you are (and you will be!) and improve your intuition about certain coding styles.***

> You should never avoid profiling in favor of a gut instinct. It is definetly worth forming a hypothesis ahead of profiling to help you learn to sport possible slow choices in your code, and you should always back up your choices with evidence

Always be driven by results that you have measured, and always start with some quick-and-dirty profiling to make sure you're addressing the right area.

Let's hypothesize that ```calculate_z_serial_purepython``` is the slowest part of the code. In that function, we do a lot of dereferencing and make many calls to basic arithmetic operators and the ```abs``` function. These will probably show up as consumers of CPU resources.

Here, we'll use the ```cProfile``` module to run a variant of the code. The output is spartan but helps us figure out where to analyze further.

The ```-s cumulative```  flag tells ```cProfile``` to sort by cumulative time spent inside each function; this gives us a view into the slowest parts of a section of code. The ```cProfile``` output is written to screen directly after our unusual ```print``` results:

```bash
$ python -m cProfile -s cumulative julia.py

Length of x: 1000
Total elements: 1
calculate_z_serial_purepython took 1.1444091796875e-05 seconds
         2037 function calls in 0.000 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.exec}
        1    0.000    0.000    0.000    0.000 julia.py:1(<module>)
        1    0.000    0.000    0.000    0.000 julia.py:11(measure_time)
        1    0.000    0.000    0.000    0.000 julia.py:21(calc_pure_python)
        3    0.000    0.000    0.000    0.000 {built-in method builtins.print}
     2002    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {method 'format' of 'str' objects}
        1    0.000    0.000    0.000    0.000 julia.py:10(timefn)
        1    0.000    0.000    0.000    0.000 julia.py:65(calculate_z_serial_purepython)
        1    0.000    0.000    0.000    0.000 functools.py:34(update_wrapper)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.abs}
        1    0.000    0.000    0.000    0.000 functools.py:64(wraps)
        7    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
        5    0.000    0.000    0.000    0.000 {built-in method builtins.setattr}
        3    0.000    0.000    0.000    0.000 {built-in method time.time}
        1    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
        4    0.000    0.000    0.000    0.000 {built-in method builtins.len}
        1    0.000    0.000    0.000    0.000 {built-in method builtins.sum}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

Sorting by cumulative time gives us an idea about where the majority of execution time is spent. This result shows us that 36.221.995 function calls occurred in just over 12 seconds (this time includes hte overhead of using ```cProfile```). Previously, our code took around 8 seconds to execute - we've just added a 4-second penalty by measuring how long each function takes to execute.

We can see that the entry point to the code ```julia.py``` on line 1 takes a total of 12 seconds. This is just the ```__main__``` call to ```calc_pure_python```. ```ncalls``` is 1, indicating that this line is executed only once.

Inside ```calc_pure_python```, the call to ```calculate_z_serial_purepython``` consumes 11 seconds. Both functions are called only once. We can drive that approximately 1 second is spent on lines of code inside ```calc_pure_python```, separate to calling the CPU-intensive ```calculate_z_serial_purepython``` function. However, we can't derive *which* lines take the time inside the function using ```cProfile```.

Inside ```calculate_z_serial_purepython```, the time spent on lines of code (without calling other functions) is 8 seconds. This function makes 34.219.980 calls to ```abs```, which take a total of 3 seconds, along with other calls that od not cost much time.

What about the ```{abs}``` call? This line is measuring the individual calls to the ```abs``` function inside ```calculate_z_serial_purepython```. While the per-call cost is negligible (it is recorded as 0.000 seconds), the total for ```34.219.980``` calls in 3 seconds. We couldn't predict in advance exactly how many calls would be made to ```abs```, as the Julia function has unpredictable dynamics.

At best we could have said that it will be called a minimum of 1 million times, as we're calculating 1000*1000 pixels. At most it will be called 300 million times, as we calculate 1000000 pixels with a maximum of 300 iterations. So 34 million calls is roughly 10% of the worst case.

If we look at the original grayscale image and, in our mind's eye, squash the white parts together and into a corner, we can estimate that the expensive white region accounts for roughly 10% of the rest of the image.

The next line in the profiled output ```{method 'append' of 'list objects{```, details the creation of 2002000 list items.

The creation of 2002000 items is occuring in ```calc_pure_python``` during the setup phase.

The ```zs``` and ```cs``` lists will be 1000*1000 items each, and these are built from a list of 1000 x and 1000 y coordinates. In total, this is 2002000 calls to append.

It is important to note that this ```cProfile``` output is not ordered by parent functions; it is summarizing the expense of all functions in the executed block of code. Figuring out what is happening on a line-by-line basis is very hard with ```cProfile```, as we get profile information only for hte function calls themselves, not for each line within the function.

Inside ```calculate_z_serial_purepython```, we can account for ```{abs}```, and in total this function costs approximately 3.1 seconds. We know that ```calculate_z_serial_purepython``` costs 11.4 seconds in total

The final line of the profiling output refers to ```lsprof```; this is the original name of the tool that evolved into ```cProfile``` and can be ignored.

To get more control over the result of ```cProfile```, we can write a statistic file and then anaylzie it in Python:

```bash
$ python -m cProfile -o profile.stats julia.py
```

## Visualizing cProfile Output with SnakeViz

```snakeviz``` is a visualizer that draws the output of ```cProfile``` as a diagram in which large boxes are areas of code that take longer to run. It replaces the older ```runsnake``` tool.

Use ```snakeviz``` to get a high-level understanding of a ```cProfile``` statistics file, particularly if you're investigating a new project for which you have little intuition. The diagram will help you visualize the CPU-usage behavior of the system , and it may highlight areas that you hadn't expected to be expensive.

To install SnakeViz, use ```$ pip install snakeviz```.

## Using line_profiler for Line-by-Line Measurements

Robert Kern's line_profiler works by profiling individual functions on a line-by-line basis, so you should start with ```cProfile``` and use the high-level view to guid which functions to profile with ```line_profiler```.

It is worthwhile printing and annotating version of the output from this tool as you modify your code, so you have a record of changes (successful or not) that you can quickly refer to. Don't rely on your memory when you're working on line-by-line changes.

To install ```line_profiler```, issue the command ```pip install line_profiler```.

A decorator (```@profile```) is used to mark the chosen function. The ```kernprof``` script is used to execute your code, and the CPU time and other statistics for each line of the chosen function are recorded.

The arguments are ```-l``` for line-by-line (rather tha function-level) profiling and ```-v``` for verbose output. Without ```-v```, you receive an ```.lprof``` output that you can later analyze with the ```line_profiler``` module.

```bash
$ kernprof -l -v julia_lineprofiler.py
```

![Line profiling](ScreenshotsForNotes/Chapter2/julia_lineprofiler_1.PNG)

Introducing ```kernprof.py``` adds a substantial amount to the runtime. In this example, ```calculate_z_serial_purepython``` takes 49 seconds; htis is up from 8 seconds using simple print statements and 12 seconds using ```cProfile```. That gain is that we get a line-by-line breakdown of where the time is spent inside the function.

The ```% Time``` column is the most helpful - we can see that 38% of the time is spent on the ```while``` testing. We don't know whether the first statement ```abs(z) < 2``` is more expensive than the second ```n < maxiter```, though. Inside the loop, we see that the update to ```z``` is also fairly expensive. Even ```n += 1``` is expensive! Python's dynamic lookup machinery is at work for every loop, even though we're using the same types for each variable in each loop - this is where compiling and type specialization gives us a massive win. The creation of th ```output``` list and the updated on line 20 are relatively cheap compared to the cost of the ```while``` loop.

If you haven't thought about the complexity of Python's dynamic machinery before, do think about what happens in that ```n += 1``` operation. Python has to check that the ```n``` object has an ```__add__``` function (and if it didn't, it'd walk up any inherited classes to see if they provided this functionality), and then the other object (1 in this case) is passed in so that the ```__add__``` function can decide how to handle the operation. Remember that the second argument might be a ```float``` or other object that may or may not be compatible. This all happens dynamically.

The obvious way to further analyze the ```while``` statement is to break it up. While there has been some discussion in the Python community around the idea of rewriting the ```.pyc``` files with more detailed information for multipart, single-line statements, we are unaware of any production tools that offer a more fine-grained analysis than ```line_profiler```.

In the following example, we break the ```while``` logic into several statements. This additional complexity will increase the runtime of the function, as we ahve more lines of code to execute, but it *might* also help us understand the costs incurred in this part of the code.

![Julia Line Profiler 2](ScreenshotsForNotes/Chapter2/julia_lineprofiler_2.PNG)

This version takes 82 seconds to execute, while the previous version took 49 seconds. Other factors *did* complicate the analysis. In this case, having extra statements that have to be executed 34219980 times each slows down the code. If we hadn't used ```kernprof.py``` to investigate the line-by-line effect of this change, we might have drawn other conclusions about the reason for the slowdown, as we'd have lacked the necessary evidence.

From this simple analysis, it looks as though the logic test of ```n``` is more than two times faster than the call to ```abs```. Since the order of evaluation for Python statements is both left to right and opportunistic, it makes sense to put the cheapest test on the left side of the equation. On 1 in every 301 tests for each coordinate, the ```n < maxiter``` test will be ```False```, so Python wouldn't need to evaluate the other side of the ```and``` operator.

We never know whether ```abs(z) < 2``` will be ```False``` until we evaluate it, and our earlier observations for this region of the complex plane suggest it is ```True``` around 10% of the time for all 300 iterations. If we wanted to have a strong understanding of the time complexity of this part of the code, it would make sense to continue the numerical analysis. In this sitatuion, however, we want an easy check to see if we can get a quick win.

We can form a new hypothesis stating, "By swapping the order of the operators in the ```while``` statement, we will achieve a reliable speedup." We *can* test this hypothesis using ```kernprof```, but the additional overhead of profiling this way might add too much noise. Instead, we can use an earlier version of the code, running a test comparing ```while abs(z) < 2``` and ```n < maxiter```: against ```while n < maxiter``` and ```abs(z) < 2```.

Running the two variants *outside* of ```line_profiler``` means they run at similar speeds. The overheads of ```line_profiler``` also confuse the result, and the results on line 17 for both version are similar. We should reject the hypothesis that in Python 3.7 changing the order of the logic results in a consistent speedup - there's no clear evidence for this.

Using a more suitable approach to solve this problem would yield greater gains.

We can be confident in our result because of the following:

* We stated a hypothesis that was easy to test.
* We changed our code so that only the hypothesis would be tested (never test two things at once!)
* We gathered enough evidence to support our conclusion.

## Using memory_profiler to Diagnose Memory Usage

Just a Robert Kern's ```line_profiler``` package measure CPU usage, the ```memory_profiler``` module by Fabian Pedregosa and Philippe Gervais measures memory usage on a line-by-line basis. Understanding the memory usage characteristics of your code allows you to ask yourself two questions:

* Could we use *less* RAM by rewriting this function to work more efficiently?
* Could we use *more* RAM and save CPU cycles by caching?

```memory_profiler``` operates in a very similar way to ```line_profiler``` but runs far more slowly. If you install the ```psutil``` package (optional but recommended), ```memory_profiler``` will run faster. Memory profiling may easily make your code run 10 to 100 times slower. In practice, you will probably use ```memory_profiler``` occasionally and ```line_profiler``` (for CPU profiling) more frequently.

Install ```memory_profiler``` with the command ```pip install memory_profiler``` (and optionally with ```pip install psutil```).

As mentioned, the implementation of ```memory_profiler``` iis not as performant as the implementation of ```line_profiler```. It may therefore make sense to run your tests on a smaller problem that completes in a useful amount of time. Overnight runs might be sensible for validation, but you need quick and reasonable iterations to diagnose problems and hypothesize solutions.

When dealing with memory allocation, you must be aware that the situation is not as clear-cut as it is with CPU usage. Generally, it is more efficient to overallocate memory in a process that can be used at leisure, as memory allocation operations are relatively expensive. Furthermore, garbage collection is not instantaneous, so object may be unavailable but still in the garbage collection pool for some time.

The outcome of this is that it is hard to really understand what is happening with memory usage and release inside a Python program, as a line of code may not allocate a deterministic amount of memory *as observed from outside the process*. Observing the gross trend over a set of lines is likely to lead to better insight than would be gained by observing the behavior of just one line.

![Memory Profiler 1](ScreenshotsForNotes/Chapter2/julia_memoryprofiler_1.PNG)
![Memory Profiler 2](ScreenshotsForNotes/Chapter2/julia_memoryprofiler_2.PNG)

Another way to visualize the change in memory use is to sample over time and plot the result. ```memory_profiler``` has a utility called ```mprof```, used once to sample the memory usage and a second time to visualize the samples. It samples by time and not by line, so it barely impacts the runtime of the code.

The following figure sis created using ```mprof run julia_memoryprofiler.py```. This writes a statistics file that is then visualized using ```mrprof plot```. Our two functions are bracketed: this shows where in time they are entered, and we can see the growth in RAM as they run. Inside ```calculate_z_serial_purepython```, we can see the steady increase in RAM usage throughout the execution of the function; this is caused by all the small objects (```int``` and ```float``` types) that are created.

![Profiler Report Using Mprof](ScreenshotsForNotes/Chapter2/ProfilerReportUsingMprof.PNG)

In addition to observing the behavior at the function level, we can add labels using a context manager. The snippet in the following example is used to generate the graph in the next figure. We can see the ```create_output_list``` label: it appears momentarily at around 1.5 seconds after ```calculate_z_serial_purepython``` and results in the process being allocated more RAM. We then pause for a second; ```time.sleep(1)```` is an artificial addition to make the graph easier to understand.

```python
@profile
def calculate_z_serial_purepython(maxiter, zs, cs):
    """Calculate output list using Julia update rule"""
    with profile.timestamp("create_output_list"):
      output = [0] * len(zs)
    time.sleep(1)
    with profile.timestamp("calculate_output"):
        for i in range(len(zs)):
            n = 0
            z = zs[i]
            c = cs[i]
            while n < maxiter and abs(z) < 2:
                z = z * z + c
                n += 1
            output[i] = n
    return output
```

In the ```calculate_output``` block that runs for most of the graph, we see a very slow, linear increase in RAM usage. This will be from all of the temporary numbers used in the inner loops. Using the labels really helps us to understand at a fine-grained level where memory is being consumed. Interestingly, we see the "peak RAM usage" line - a dashed vertical line just before the 10-second mark - occurring before the termination of the program. Potentially this is due to the garbage collector recovering some RAM from the temporary objects used during ```calculate_output```.

What happens if we simplify our code and remove the creation of the ```zs``` and ```cs``` lists? We then have to calculate these coordinates inside ```calculate_z_serial_purepython``` (so the same work is performed), but we'll save RAM by not storing them in lists.

![Profiling Report using Mrpof with Labels](ScreenshotsForNotes/Chapter2/ProfilerReportUsingMprofWithLabels.PNG)

In the next figure, we see a major change in behavior - the overall envelope of RAM usage drops from 140 MB to 60 MB, reducing our RAM usage by half!

![Profiling Report after removing two large lists](ScreenshotsForNotes/Chapter2/ProfilerReportAfterRemovingTwoLargeLists.PNG)

## Introspecting an existing process with PySpy

```py-spy``` is an intriguing new sampling profiler - rather than requiring any code changes, it introspects an already-running Python process and reports in the console with a ```top```-like display. Being a sampling profiler, it has almost no runtime impact on your code. It is written in Rust and requires elevated privileges to introspect another process.

This tool could be very useful in a production environment with long-running processes or complicated installation requirements. It supports Windows, Mac, and Linux. Install it using ```pip install py-spy``````. If your process is already running, you'll want to use ```ps``` to get its process identifier (the PID); then this can be passed into ```py-spy```.

## Bytecode: Under the Hood

### Using the ```dis``` Module to Examine CPython Bytecode

The ```dis``` module lets us inspect the underlying bytecode that we run inside the stack-based CPython virtual machine. Having an understanding of what's happening in the virtual machine that runs your higher-level Python code will help you to understand why some styles of coding are faster than other. It will also help when you come to use a tool like Cython, which steps outside of Python and generates C code.

The ```dis``` module is built in. You can pass it code or a module, and it will print out a disassembly.

### Different approaches, different complexity

There will be various ways to express your ideas using Python. Generally, the most sensible option should be clear, but if your experience is primarily with an older version of Python or another programming language, you may have other methods in mind. Some of these ways of expressing an idea may be slower than others.

You probably care more about readability than speed for most of your code, so your team can code efficiently without being puzzled by performant but opaque code.

Sometimes you will want performance, though (without sacrificing readability). Some speed testing might be what you need.

Take a look at the following two code snippets. Both do the same job, but the first generates a lot of additional Python bytecode, which will cause more overhead.

```python
def fn_expressive(upper=1_000_000):
    total = 0
    for n in range(upper):
        total += n
    return total


def fn_terse(upper=1_000_000):
    return sum(range(upper))
```

Both functions calculate the sum of a range of integers. A simple rule of thumb (but one you *must* back up using profiling!) is that more lines of bytecode will execute more slowly than fewer equivalent lines of bytecode that use built-in functions.

If we use the ```dis``` module to investigate the code for each function, as shown in the following example, we can see that the virtual machine has 17 lines to execute with the more expressive function and only 6 to execute with the very readable but terse second function:

```
- dis.dis(fn_expressive)

  4           0 LOAD_CONST               1 (0)
              2 STORE_FAST               1 (total)

  5           4 LOAD_GLOBAL              0 (range)
              6 LOAD_FAST                0 (upper)
              8 CALL_FUNCTION            1
             10 GET_ITER
        >>   12 FOR_ITER                 6 (to 26)
             14 STORE_FAST               2 (n)

  6          16 LOAD_FAST                1 (total)
             18 LOAD_FAST                2 (n)
             20 INPLACE_ADD
             22 STORE_FAST               1 (total)
             24 JUMP_ABSOLUTE            6 (to 12)

  7     >>   26 LOAD_FAST                1 (total)
             28 RETURN_VALUE
```

```
- dis.dis(fn_terse)

 11           0 LOAD_GLOBAL              0 (sum)
              2 LOAD_GLOBAL              1 (range)
              4 LOAD_FAST                0 (upper)
              6 CALL_FUNCTION            1
              8 CALL_FUNCTION            1
             10 RETURN_VALUE
```

The difference between the two code blocks is striking. Inside ```fn_expressive()```, we maintain two local variables and iterate over a list using a ```for``` statement. The ```for``` loop will be checking to see if a ```StopIteration``` exception has been raised on each loop. Each iteration applies the ```total.__add__``` function, which will check the type of the second variable (```n```) for each iteration. These checks all add a little expense.

Inside ```fn_terse()```, we call out to an optimized C list comprehension function that knows how to generate the final result without creating intermediate Python objects. This is much faster, although each iteration must still check for the types of the objects that are being added together.

As noted previously, you *must* profile your code - if you just rely on this heuristic, you will inevitably write slower code at some point. It is definitely worth learning whether a shorter and still readable way to solve your problem is built into Python. If so, it is more likely to be easily readable by another programmer, and it will *probably* run faster.

### Unit testing during optimization to maintain correctness

Add unit tests to your code for a saner life. You'll be giving your current self and your colleagues faith that your code works, and you'll be giving a present to your future-self who has to maintain this code later. You really will save a lot of time in the long term by adding tests to your code.

In addition to unit testing, you should also strongly consider using ```coverage.py```. It checks to see which lines of code are exercise by your tests and identifies the sections that have no coverage. This quickly lets you figure out whether you're testing the code that you're about to optimize, such that any mistakes that might creep in during the optimization process are quickly caught.

## Strategies to Profile Your Code Successfully

Profiling requires some time and concentration. You will stand a better chance of understanding your code if you separate the section you want to test from the main body of your code. YOu can then unit test hte code to preserve correctness, and you can pass in realistic fabricated data to exercise the inefficiencies you want to address.

Do remember to disable any BIOS-based accelerators, as they will only confuse your results.

Your operating system may also control the clock speed - a laptop on battery power is likely to more aggressively control CPU speed than a laptop on AC power. To create a more stable benchmarking configuration, we do the following:

* Disable Turbo Boost in the BIOS.
* Disable the operating system's ability to override the SpeedStep (you will find this in your BIOS if you're allowed to control it.)
* Use only AC power (never battery power)
* Disable background tools like backups and Dropbox while running experiments.
* Run the experiments many times to obtain a stable measurement.
* Possibly drop to run level 1 (Unix) so that no other tasks are running.
* Reboot and rerun the experiments to double-confirm the results.

Try to hypothesize the expected behavior of your code and then validate (or disprove!) the hypothesis with the result of a profiling step. Your choices will not change (you should only drive your decisions by using the profiled results), but your intuitive understanding of the code will improve, and this will pay off in future projects as you will be more likely to make performant decisions. Of course, you will verify these performant decisions by profiling as you go.

Do not skimp on the preparation. If you try to performance test code deep inside a large project without separating it from the larger project, you are likely to witness side effects that will sidetrack your efforts. It is likely to be harder to unit test a large project when you're making fine-grained changes, and this may further hamper your efforts. Side effects could include other threads and processes impacting CPU and memory usage and networking and disk activity, which will skew your results.

Naturally, you're already using source code control, so you'll be able to run multiple experiments in different branches without ever losning "the version that work well."

For web servers, investigate *dowser* and *dozer*; you can use these to visualize in real time the behavior of objects in the namespace. Definitely consider separating the code you want to test out of the main web application if possible, as this will make profiling significantly easier.

Make sure your unit tests exercise all the code paths in the code that you're analyzing. Anything you don't test that is used in your benchmarking may cause subtle errors that will slow down your progress. Use ```coverage.py``` to confirm that your tests are covering all the code paths.

Unit testing a complicated section of code that generates a large numerical output may be difficult. Do not be afraid to output a text file of results to run though ```diff``` or to use a ```pickled``` object.

If your code might be subject to numerical rounding issues due to subtle changes, you are better off with a large output that can be used for a before-and-after comparison. One cause of rounding errors is the difference in floating-point precision between CPU registers and main memory. Running your code through a different code path can cause subtle rounding errors that might later confound you - it is better to be aware of this as soon as they occur.

Obviously, it makes sense to use a source code control tool while you are profiling and optimizing. Branching is cheap, and it will preserve your sanity.

## 3. List and Tuples

```>```

## Introduction

Lists and tuple are a class of data structures called ```arrays```. An array is a flat list of data with some intrinsic ordering. Usually in these srots of data structures, the relative ordering of the elements is as important as the elements themslevs. In addition, this a *priori* knowledge of the ordering is incredibly valuable: by konwing that data in our array is at a specific position, we can retrieve it on O(1)! There are also many ways to implement arrays, and each solution has its own useful features and guarantees. This is why in Python we have two types of arrays: lists and tuples. *Lists* are dynamic arrays that let us modify and resize the data we are storing, while *tuples* are static arrays whose contents are fixed and immutable.

Let's unapck these previous statements a bit. System memory on a computer can be thought of as a series of numbered buckets, each capable of holding a number. Python stores data in these bukcets *by reference*, which means the number itself simply points to, or refers to, the data we actually care about. As a result, these buckets can store any type of data we want (as opposed to *numpy* arrays, which have static type and can store only that type of data).

When we want to create an array (and thus a list or utple), we first have to allocate block of system memory (where every section of this block will be used as an integer-sized pointer to actual data). his involves going to the system kernle and requesting the use of ```N``` *consecutive* blocks. The following figure shows an example of the system meory layout for an array (in this case, a list) of size 6:

![Memory Layout Example](ScreenshotsForNotes/Chapter3/memory_example.PNG)

In order to look up any specific element in our list, we simply need to know which element we want and remember which bucket our data strated in. Since all of the data will occupy the same amount of space (one "bucket", or, more specifically, one integer-sized pointer to the actual data), we don't need to know naything about the type of data that is being stored to do this calculation.

If, for example, we needed to retreive the zeroth element in our array, we woul simply go to the first bucket in our sequence, ```M```, and read out the value inside it. If,on hte other hand, we needed the fifth element in our array, we would go to the bucket at position ```M+5``` and read its content. In general, if we want to retrieve element ```i``` from our array, we go to bucket ```M+i```. So, by ahving our data stored in consecutive buckets, and having knowledge of the ordering of our data, we can lcoate our data by knowing which bucket to look at in one step (or ```O(1)```), regardless of how big our array is.

## Tuples as static arrays

Tuples are fixed and immutable. This means that once a tuple is created, unilke a list, it cannot be modified or resized:

```Python
>>> t = (1, 2, 3, 4)
>>> t[0] = 5

...
TypeError: 'tuple' object does not support item assignment
```

However, although they don't support resizing, we can concatenate two tuples together and form a new tuple. The operation is similar to the ```resize``` operation on lists, but we do not allocat any extra space for the resulting tuple:

```Python
>>> t1 = (1, 2, 3, 4)
>>> t2 = (5, 6, 7, 8)
>>> t1 + t2
(1, 2, 3, 4, 5, 6, 7, 8)
```

If we consider this to be compraable to the ```append``` operation on lists, we see that it performs in ```O(n)``` as opposed to the ```O(1)``` speed o lists. This is because we must allocate and copy the tuple every time something is added to it, as opposed to only when our extra headroom ran out for lists. As a result of this, there is no in-place ```append```-like operation; adding two tuples always returns a new tuple that is in a new location in memory.

Not storing the extra headroom for resizing has the advantage of using fewer reousrces. A list of size 100000000 craeted with any ```append``` operation actually uses 112500007 elements' writh of memory, while a tuple holding the same data will only ever use exactly 100000000 elements' worth of memory. This makes tuple lightweight and preferable when data becomes static.

Furthermore, even if we create a list *without* ```append``` (and thus we don't have the extra headroom introduced by an ```append``` operation), it will *still* be larger in memory than a tuple with the same data. This is because lists have to keep track of more informatino about their current state in order to efficiently resize. Whiel thie extra informatino is quite small (the quievalent of one extra element), it can add up if several million lists are in use.

Another benefit of the static nature of tuple is something Python does in the backgorund: resource caching. Python is garbage collected, which means that when a variable isn't used anymore, Python frees the memory used by that variable, giving it back to the operatin system for use in other applications (or for other variables). For tuples of sizes 1-20, however, when they are no longer in use, the space isn't immediately given back to the ystem: up to 20000 of each size are saved for future use. This means that when a new tuple of that size is needed in the future, we don't need to communicate with the operation system to find a region in memory to put the data into, since we ahve a reserve of free memory already. However, this also means that the Python process will have some extra memory overhead.

While this may seem like a small benefit, it is one of the fantastic things about tuples: tehy can be created easily and quickly since they can avoid communications with the operation system, which can cost your program quite a bit of time.

# 4. Dictionaries and Sets

```>```

## What are sets and dictionaries known for

**Sets and dictionaries are ideal data structuresto be used when your data has no intrinsic order (except for insertion order) but does have a unique object that can be used to reference it (ther eference object is normally a string, but it can be any hashable type)**. This refernece object is called the *key*, while the data is the *value*. Dictionaries and sets are almost identical, except that sets do not actually contain values: a set is simply a collection of unique keys. As the name implies, sets are very sueful for doing set operations.

While we saw in the previous chapter that we are restricted to, at best, ```O(log n)``` lookup time on lists/tuples with no intrinsic order (through a search operation), dictionaries and sets give us ```O(1)``` lokups based on the arbitrary index. In addition, like lists/tuples, dictionaries and sets have ```O(1)``` insertion time. This speed is accomplished through the use of an open address hash table as the underlying data structure.

However, there is a cost to using dictionaries and sets. First, they generally take up a larger footprint in memory. Also, although the complexity for insertions/lookups is ```O(1)```, the actual speed depends greatly on the hasing function that is in use. If the has function is slow to evaluate, any operations on dictionaries or sets will be similarly slow.


## What is a *hashable* type

A *hashable* type os one that implements both the ```__hash__``` magic function and either ```__eq__``` or ```__cmp__```. All native types in Python already implement ehese, and any user classes have default values.
The ```__cmp__()``` special method is no longer honored in Python 3.

## How dictionaries and sets work

Dictionaries and sets use *hash tables* to achieve their ```O(1)``` lookups and insertions. This efficiency is the result of a very clever uesage of a hash function to turn an arbitrary key (i.e., a string or ojbect) into an index for a list. The hash function and list can later be used to determine where any particular piece of data is right away, without a search. By turning the dat'as key into something that can be used like a list index, we can get the same performance as with a list. IN addition, instead of having to refere to data by a numerical index, which itself implies some ordering to the data, we can refer to it by this arbitrary key.

## Inserting and Retrieving

To create a hash table from scratch, we start with some allocated memory, similar to what we started with for arrays. For an array, if we want to insert data, we simply find the smallest unused bucket and insert our data there (and resize if necessary). For hash tables, we must first figure out the placement of the data in this contiguous chunk of memory.

The placement of the new data is contingent of two properties of the data we are inserting: the hashed value of the key and how the value compares to other objects. This is because when we insert data, the key is first hashed and masked so that it turns into an effective index in an array. 

A *mask* is a binary number that truncates the value of a number. So ```0b1111101 & 0b111 = 0b101 = 5``` represents the operation of ```0b111``` masking the number ```0b1111101```. This operation can also be thought of as taking a certain number of the least-significant digits of a number.

The mask makes sure that the hash value, whidch can take the value of any integer, fits within the allocated number of buckets. So if we have allocated 8 blocks of memory and our hash value is ```28975```, we consider the bubkcet at index ```28975 & 0b111 = 7```. If, however, our dictionary has grown to require 512 blocks of memory, the mask becomes ```0b111111111``` (and in this case, we would consider the bucket at index ```28975 & 0b111111111```).

Now we must check if this bucket is already in use. If it is empty, we can insert the key and the vlaue into this block of memory. We store the key so that we can make sure we are retrieving the correct value on lookups. If it is in use and the value of the bucket is equal to the value we wish to insert (a comparison done with the ```cmp``` built-in), then the key/value pair is already in the hash table and we can return . However, if the values don't match, we must find a new place to put the data. 

As an extra optimization, Python first appends the key/value data into a standard array and then stores only the *index* into this array in the hash table. This allows us to reduce the amount of memory used by 30-95%. In addition, this gives us the interesting proeprty taht we keep a record of the order which new items were added into the dictionary.

To find the new index, we compute is using a simple linear function, am ethod called *probing*. Python's probing mmechanism adds a contribution from the higher-order bits of the original hash (recall that for a table of length 8 we consider only the last there bits of the hash for the initial index, through the use of a mask value of ```mask = 0b111 = bin(8-1))```. Using these higher-order bits gives each has a different sequence of next possible hashes, which helps to avoid future collisions.

There is a lot of freedom when pickign the algorithm to generate a new index; however, it is quite important that the scheme visits every possible index in order to evenly distribute the data in the table. How well distributed the data is throughout the hash table is called the *load factor* and is related to the entropy of the ahs function. The pseudocode in the following example illustrates the calculation of hash indices used in CPython 3.7. This also shows an interesting fact about hash tables: most of the storage space they have is empty!

```Python
def index_sequence(key, mask = 0b111, PERTURB_SHIFT=5):
    perturb = hash(key)
    i = perturb & mask
    yield i
    while True:
      perturb >>= PERTURB_SHIFT
      i = (i * 5 + pertrub + 1) & mask
      yield i
```

This probing is a modification of the naive method of *linear probing*. In linearg probing, we simply yield the values ```i = (i * 5 + pertrub + 1) && mask```, where ```i``` is initialized to the has hvalue of the key. The value of ```5``` comes from the properties of a linear congruential generator (LCG), which is used in generating random numbers. An important thing to node is that linear probing deals only wit hthe last several bits of the hash and disregards the rest (i.e., for a dictionary with eight elements, we look only at the last three bits since at that point the mask is ```0x111```). This means that if hashing two items gives teh same last three binary digits, we will not only have a colllision, but also the sequence of probed indices will be teh same. The perturbed scheme that Python uses will start taking into consideration more bits from the items' hashes to resolve this problem.

A similar producer is done when we are performing lookups on a specific key: the given key is transformed into an index, and that index is examined. If the key in that index matches (recall that we also store the original key when doing insert operations), then we can return the value. If it doesn't, we keep creating new indices using the same scheme, until we weither find the data or hit an empty bucket. If we hit an empty bucket, we can conclude that the data does not exist in the table.

The following figure illustrates the process of adding data into a hash table. Here, we choose to create a hash function that simply uses the first letter of the input. We accomplish this by using Python's ```ord``` function on the first letter of hte input to get the integer representationg of that letter (recall that hash functions must return integers).

![Resulting hash table from inserting with collisions](ScreenshotsForNotes/Chapter4/ResultingHashTableFromInsertingWithCollisions.PNG)

```Python
class City(str):
    def __hash__(self):
        return ord(self[0])


# We createa  dictionary where we assign arbitrary values to cities
data = {
    City("Rome"): "Italy",
    City("San Francisco"): "USA",
    City("New York"): "USA",
    City("Barcelona"): "Spain",
}
```

In thsi case, ```Barcelona``` and ```Rome``` cause the hash collision (The figure above shows the outcome of this insertion). We see this because, for a dictionary with four elements, we have a mask value of ```0b111```. As a result, ```Barcelona``` and ```Rome``` will try to use the same index:

```Python
hash("Barcelona") = ord("B") & 0b111
                  = 66 & 0b111
                  = 0b1000010 & 0b111
                  = 0b010 = 2

hash("Rome") = ord("R") & 0b111
             = 82 & 0b111
             = 0b1010010 & 0b111
             = 0b010 = 2
```

## Deletion

When a value is deleted from a hash table, we cannot simply write a ```NULL``` to that bucket of memory. This is because we ahve used ```NULL```s as a sentinel value while probing for hash collisions. As a result, we must write a special value that signifies that the bucket is empty, but there still may be values after it to consider when resolving a hash collision. So if "Rome" was deelted from the dictionary, subsequente lookups for "Barcelona" will first see this sentinel value where "Rome" used to be and instead of stopping, continue to check the next indices given by the ```index_sequence```. These empty slots ca be written ot in the future and are removed when the hash table is resized.

## Resizing

As mroe items are inserted into the hash table, the table itself must be resized to accommodate them. It can be shwon that a table that is no more htan two-thrids full will have optimal space savings while still having a good obund on the number of collisions to expect. Thus, when a table resaches this critical point, it is grown. To do this, a larger table is allocated (i.e., more buckets in memory are reserved), the mask is adjusted to fit the new table, and all elements of the old table are reinserted into the new one. This requires recomputing indices, since the changed mask will change the resulting index. As a result, resizing large hash tables can be quite expensive! However, since we do this resizing operaiton only when the table is too mslal, as opposed to doing it on every insert, the amortized cost of an insert is still ```O(1)```.

By default, the smallest size of a dictionary or set is 8 (that is, if you are storing only three values, Python will still allocate eight elements), and it will resize by 3x if the dictionary is more than two-thirds full. So once hte sixth item is being inserted into the originally empty dictionary, it wil lbe resized to hold 18 elements. At this piont, once the 13th element is insrted into the object, it wil be resized to 39, then 81, and so on, always increasing the size by 3x. This gives us the following possible sizes:

```8; 18; 39; 81; 165; 333; 669; 1,341; 2,682; 5,373; 10,749; 21,501; 43,005;...```

It is important to note that resizing can happne to make a hahs table large *or* smaller. That is, if sufficicently many elements of a hash table are deleted, the table can be scaled down in size. However, ***resizing happens only during an insert***.

## Hash Functions and Entropy

Objects in Python are generally hashable, since they already have built-in ```__hash__``` and ```__cmp__``` functions asssociated with them. For numerical types (```int``` and ```float```), the hash is based simply on the bit value of the number they represent. Tuplse and strings have a hash value that is based on their contents. Lists, on the other hand, do not support hasing because their values can change. Since a list's values can change, so could the has that represents the list, whcih would hcange the relative placement of that key in the hash table.

User-defined classes also have default hash and comparison functions. The default ```__hash__``` function simply returns the object's placement in memory as given by the built-in ```id``` function. Similarly, the ```__cmp__``` operator compoares the numerical value of the object's placement in memory.

This is generally acceptable, sinc etwo instance of a calss are generally different and should not collied in a hash table. However, ins ome cases we would like to sue ```set``` or ```dict``` objects to disambiguate between items. Take the following class definition:

```Python
class Point():
    def __init__(self, x, y):
        self.x, self.y = x, y
```

If we were to instantiate multiple ```Point``` objects with the same values for ```x``` and ```y```, they would all be independent objects in memory nad thus have different placements in memory, which owuld give them all different hash values. This means that putting them all into a ```set``` would result in all of them having individual entries:

```Python
>>> p1 = Point(1, 1)
>>> p2 = Point(1, 1)
>>> set([p1, p2])
set([<__main__.Point at 0x1099bfc90>, <__main__.Point at 0x1099bfbd0>])
>>> Point(1, 1) in set([p1, p2])
False
```

We can remedy this by forming a custom hash function that is based on the actual contents of the object as opposed to the object's placement in memory. The hash function can be any function as long as it consistently gives the same result for the same object (there are also considerations regarding the entropy of the hashing function, which we will discuss later.) The following redefinition of the ```Point``` class will yield the results we expect:

```Python
class Point():
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
```

This allows us to create netires in a set or dictionary indexed by the properties of the ```Point``` object rahter than the memory address of the instantiated object:

```Python
>>> p1 = Point(1, 1)
>>> p2 = Point(1, 1)
>>> set([p1, p2])
set([<__main__.Point at 0x109b95910>])
>>> Point(1, 1) in set([p1, p2])
True
```

As alluded to when we discussed hash collisions, a custom-selected hash function should be careful to evenly distributed hash values in order to avoid collisions. Having many collisions will degarde the performance of a hash table: if most keys have collisions, we need to constnatly "probe" the other values, effectively walking a potentially large oprtion of the dictionary to find the key in question. In the wordst case, when all keys in a dictionary collide, the performance of lookups in the dictionary is ```O(n)``` and thus the same as if we were searching through a list.

If we know that we are storing 5000 values in a dictionary and we need to create a hashing function for the object we wish to use as a key, we must be aware that the dictionary willbe stored in a hash table of size 16384 and thus only the last 14 bits of our hash are being used to create an index (for a ahsh table if this size, the mask is ```bin(16_384 - 1) = 0b11111111111111```).

This idea of "hwo well distribuetd my hash function is" is called the ***entropy of the hash function****. Entropy is defined as

![Entropy of hash functions](ScreenshotsForNotes/Chapter4/EntropyOfHashFunction.PNG)

where ```p(i)``` is the probability that hte hash function gives hash ```i```. It is maximized when every hash value has equal probability of being chosen. A hash function that maximizes entropy is called an *ideal* hash function since it guarnatees the minimal number of collisions.

For an infinitely large dictionary, the hash function used for integers is ideal. This is becaused the hash value for an integer is simply the integer itself! For an infinitely large dictionary, the mask valeu is inifnite, and thus we consider all bits in the hash value. Therefore, given any two nubmers, we can guarantee that their hash values will not be the same.

However, if we made this dictionary finite, we would no loner have this guarantee. For example, for a dictionary with four elements, the mask we use is ```0b111```. Thsu the has hvalue for the number ```5``` is ```5 & 0b111 = 5```, and the ahs value for ```501``` is ```501 & 0b111 = 5````, and so their entries will collide.

To find the mask for a dictionary with an arbitrary number of elements, ```N```, we first find the minimum number of buckets that dicitonary must have to still be two-third full (```N * (2 / 3 + 1)```). Then we find the smallest dictionary size that will hold this number of elements (8; 32; 128; 512; 2048; etc.) and find the number of bits necessary to hold this number. For example, if ```N=1039```, then we must have at least 1731 buckets, which means we need a dictionary with 2048 buckets. Thus the jmask is ```bin(2048 - 1) = 0b11111111111```.

Ther eis no single best hash function to use when using a finite dictionary. However, knonwing up front what range of value swill be used and how large the ditionary will be helps in makinga good selection. For example, if we are storign all 676 combinations of two lowercase letters as keys in a dictionary (```aa```, ```ab```, ```ac```, etc.), a good hashing function would be the one shown in the following example:

```Python
def twoletter_hash(key):
    offset = ord('a')
    k1, k2 = key
    return (ord(k2) - offset) + 26 * (ord(k1) - offset)
```

Thsi gives no hash collisions for any combination of two lowercase letters, considering a mask of ```0b11111111111``` ( adictionary of 676 values will be held in a hash table of length 2048, which has a mask of ```bin(2048 - 1) = 0b11111111111```).

## Dictionaries and Namespaces

Doing a lookup on a dictionary is fast; hwoever, doing it uunnecessarily will slow down your code, just as any extraneous lines will. One area where this surfaces is in Python's namespace management, which heavily uses dictionaries to do its lookups.

Whenver a variable, function, or module is invoked in Python, there is a hierarchy that determines where it looks for these objects. First, Python look inside the ```locals()``` array, which ahs entires for all local variables. Python works hard to make local variables lookups fast, and this is the only part of the chain that doesn't require a dictionary lookup. If it doesn't exist there, the ```globals()``` dictionary is searched. Finally, if the object isn't found there, the ```__builtin__``` object is searched. It is important to note that while ```locals()``` and ```globals9)``` are explicitly dictionaries and ```__builtin__``` is technically a mdoule object, when searching ```__builtin__``` for a given property ,we are just doing a dictionary lookup inside *its* ```locals()``` map (this is the case for all module objects and class objects!).

# 5. Iterators and Generators

Since I've already talked about iterators and generators in the previous books, I will now just write down every single method in the ```itertools``` module since I've already went through iterators and generators in Python

## Infinite Iterators

### ```itertools.count(start=0, step=1)```

Make an iterator that returns evenly spaced values starting with number start. Often used as an argument to ```map()``` to generate consecutive data points. Also, used with ```zip()``` to add sequence numbers. Roughly equivalent to:

```Python
def count(start=0, step=1):
    # count(10) --> 10 11 12 13 14 ...
    # count(2.5, 0.5) -> 2.5 3.0 3.5 ...
    n = start
    while True:
        yield n
        n += step
```

When counting with floating point numbers, better accuracy can sometimes be achieved by substituting multiplicative code such as: ```(start + step * i for i in count())```.

### ```itertools.cycle(iterable)```

ake an iterator returning elements from the iterable and saving a copy of each. When the iterable is exhausted, return elements from the saved copy. Repeats indefinitely. Roughly equivalent to:

```Python
def cycle(iterable):
    # cycle('ABCD') --> A B C D A B C D A B C D ...
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
              yield element
```

Note, this member of the toolkit may require significant auxiliary storage (depending on the length of the iterable).

### ```itertools.repeat(object[, times])```

Make an iterator that returns object over and over again. Runs indefinitely unless the times argument is specified. Used as argument to ```map()``` for invariant parameters to the called function. Also used with ```zip()``` to create an invariant part of a tuple record.

Roughly equivalent to:

```Python
def repeat(object, times=None):
    # repeat(10, 3) --> 10 10 10
    if times is None:
        while True:
            yield object
    else:
        for i in range(times):
            yield object
```

A common use for repeat is to supply a stream of constant values to ```map``` or ```zip```:

```Python
>>>
>>> list(map(pow, range(10), repeat(2)))
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

## Iterators terminating on the shortest input sequence

### ```itertools.accumulate(iterable[, func, *, initial=None])```

Make an iterator that returns accumulated sums, or accumulated results of other binary functions (specified via the optional func argument).

If func is supplied, it should be a function of two arguments. Elements of the input iterable may be any type that can be accepted as arguments to func. (For example, with the default operation of addition, elements may be any addable type including Decimal or Fraction.)

Usually, the number of elements output matches the input iterable. However, if the keyword argument initial is provided, the accumulation leads off with the initial value so that the output has one more element than the input iterable.

Roughly equivalent to:

```Python
def accumulate(iterable, func=operator.add, *, initial=None):
    'Return running totals'
    # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
    # accumulate([1,2,3,4,5], initial=100) --> 100 101 103 106 110 115
    # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
    it = iter(iterable)
    total = initial
    if initial is None:
        try:
            total = next(it)
        except StopIteration:
            return
    yield total
    for element in it:
        total = func(total, element)
        yield total
```

There are a number of uses for the func argument. It can be set to min() for a running minimum, max() for a running maximum, or operator.mul() for a running product. Amortization tables can be built by accumulating interest and applying payments. First-order recurrence relations can be modeled by supplying the initial value in the iterable and using only the accumulated total in func argument:

```Python
>>> data = [3, 4, 6, 2, 1, 9, 0, 7, 5, 8]
>>> list(accumulate(data, operator.mul))     # running product
[3, 12, 72, 144, 144, 1296, 0, 0, 0, 0]
>>> list(accumulate(data, max))              # running maximum
[3, 4, 6, 6, 6, 9, 9, 9, 9, 9]

# Amortize a 5% loan of 1000 with 4 annual payments of 90
>>> cashflows = [1000, -90, -90, -90, -90]
>>> list(accumulate(cashflows, lambda bal, pmt: bal*1.05 + pmt))
[1000, 960.0, 918.0, 873.9000000000001, 827.5950000000001]

# Chaotic recurrence relation https://en.wikipedia.org/wiki/Logistic_map
>>> logistic_map = lambda x, _:  r * x * (1 - x)
>>> r = 3.8
>>> x0 = 0.4
>>> inputs = repeat(x0, 36)     # only the initial value is used
>>> [format(x, '.2f') for x in accumulate(inputs, logistic_map)]
['0.40', '0.91', '0.30', '0.81', '0.60', '0.92', '0.29', '0.79', '0.63',
 '0.88', '0.39', '0.90', '0.33', '0.84', '0.52', '0.95', '0.18', '0.57',
 '0.93', '0.25', '0.71', '0.79', '0.63', '0.88', '0.39', '0.91', '0.32',
 '0.83', '0.54', '0.95', '0.20', '0.60', '0.91', '0.30', '0.80', '0.60']
```

See functools.reduce() for a similar function that returns only the final accumulated value.

### ```itertools.chain(*iterables)```

Make an iterator that returns elements from the first iterable until it is exhausted, then proceeds to the next iterable, until all of the iterables are exhausted. Used for treating consecutive sequences as a single sequence. Roughly equivalent to:

```Python
def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

### ```classmethod chain.from_iterable(iterable)```

Alternate constructor for chain(). Gets chained inputs from a single iterable argument that is evaluated lazily. Roughly equivalent to:

```Python
def from_iterable(iterables):
    # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

### ```itertools.compress(data, selectors)```

Make an iterator that filters elements from data returning only those that have a corresponding element in selectors that evaluates to True. Stops when either the data or selectors iterables has been exhausted. Roughly equivalent to:

```Python
def compress(data, selectors):
    # compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
    return (d for d, s in zip(data, selectors) if s)
```

### ```itertools.dropwhile(predicate, iterable)```

Make an iterator that drops elements from the iterable as long as the predicate is true; afterwards, returns every element. Note, the iterator does not produce any output until the predicate first becomes false, so it may have a lengthy start-up time. Roughly equivalent to:

```Python
def dropwhile(predicate, iterable):
    # dropwhile(lambda x: x<5, [1,4,6,4,1]) --> 6 4 1
    iterable = iter(iterable)
    for x in iterable:
        if not predicate(x):
            yield x
            break
    for x in iterable:
        yield x
```

### ```itertools.filterfalse(predicate, iterable)```

Make an iterator that filters elements from iterable returning only those for which the predicate is False. If predicate is None, return the items that are false. Roughly equivalent to:

```Python
def filterfalse(predicate, iterable):
    # filterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x
```

### ```itertools.groupby(iterable, key=None)```

Make an iterator that returns consecutive keys and groups from the iterable. The key is a function computing a key value for each element. If not specified or is None, key defaults to an identity function and returns the element unchanged. Generally, the iterable needs to already be sorted on the same key function.

The operation of groupby() is similar to the uniq filter in Unix. It generates a break or new group every time the value of the key function changes (which is why it is usually necessary to have sorted the data using the same key function). That behavior differs from SQL’s GROUP BY which aggregates common elements regardless of their input order.

The returned group is itself an iterator that shares the underlying iterable with groupby(). Because the source is shared, when the groupby() object is advanced, the previous group is no longer visible. So, if that data is needed later, it should be stored as a list:

```Python
groups = []
uniquekeys = []
data = sorted(data, key=keyfunc)
for k, g in groupby(data, keyfunc):
    groups.append(list(g))      # Store group iterator as a list
    uniquekeys.append(k)
```

groupby() is roughly equivalent to:

```Python
class groupby:
    # [k for k, g in groupby('AAAABBBCCDAABBB')] --> A B C D A B
    # [list(g) for k, g in groupby('AAAABBBCCD')] --> AAAA BBB CC D
    def __init__(self, iterable, key=None):
        if key is None:
            key = lambda x: x
        self.keyfunc = key
        self.it = iter(iterable)
        self.tgtkey = self.currkey = self.currvalue = object()
    def __iter__(self):
        return self
    def __next__(self):
        self.id = object()
        while self.currkey == self.tgtkey:
            self.currvalue = next(self.it)    # Exit on StopIteration
            self.currkey = self.keyfunc(self.currvalue)
        self.tgtkey = self.currkey
        return (self.currkey, self._grouper(self.tgtkey, self.id))
    def _grouper(self, tgtkey, id):
        while self.id is id and self.currkey == tgtkey:
            yield self.currvalue
            try:
                self.currvalue = next(self.it)
            except StopIteration:
                return
            self.currkey = self.keyfunc(self.currvalue)
```

### ```itertools.islice(iterable, stop)```
### ```itertools.islice(iterable, start, stop[, step])```

Make an iterator that returns selected elements from the iterable. If start is non-zero, then elements from the iterable are skipped until start is reached. Afterward, elements are returned consecutively unless step is set higher than one which results in items being skipped. If stop is None, then iteration continues until the iterator is exhausted, if at all; otherwise, it stops at the specified position. Unlike regular slicing, islice() does not support negative values for start, stop, or step. Can be used to extract related fields from data where the internal structure has been flattened (for example, a multi-line report may list a name field on every third line). Roughly equivalent to:

```Python
def islice(iterable, *args):
    # islice('ABCDEFG', 2) --> A B
    # islice('ABCDEFG', 2, 4) --> C D
    # islice('ABCDEFG', 2, None) --> C D E F G
    # islice('ABCDEFG', 0, None, 2) --> A C E G
    s = slice(*args)
    start, stop, step = s.start or 0, s.stop or sys.maxsize, s.step or 1
    it = iter(range(start, stop, step))
    try:
        nexti = next(it)
    except StopIteration:
        # Consume *iterable* up to the *start* position.
        for i, element in zip(range(start), iterable):
            pass
        return
    try:
        for i, element in enumerate(iterable):
            if i == nexti:
                yield element
                nexti = next(it)
    except StopIteration:
        # Consume to *stop*.
        for i, element in zip(range(i + 1, stop), iterable):
            pass
```

If start is None, then iteration starts at zero. If step is None, then the step defaults to one.

### ```itertools.pairwise(iterable)```

Return successive overlapping pairs taken from the input iterable.

The number of 2-tuples in the output iterator will be one fewer than the number of inputs. It will be empty if the input iterable has fewer than two values.

Roughly equivalent to:

```Python
def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
```

### ```itertools.starmap(function, iterable)```

Make an iterator that computes the function using arguments obtained from the iterable. Used instead of map() when argument parameters are already grouped in tuples from a single iterable (the data has been “pre-zipped”). The difference between map() and starmap() parallels the distinction between function(a,b) and function(*c). Roughly equivalent to:

```Python
def starmap(function, iterable):
    # starmap(pow, [(2,5), (3,2), (10,3)]) --> 32 9 1000
    for args in iterable:
        yield function(*args)
```

### ```itertools.takewhile(predicate, iterable)```

Make an iterator that returns elements from the iterable as long as the predicate is true. Roughly equivalent to:

```Python
def takewhile(predicate, iterable):
    # takewhile(lambda x: x<5, [1,4,6,4,1]) --> 1 4
    for x in iterable:
        if predicate(x):
            yield x
        else:
            break
```

### ```itertools.tee(iterable, n=2)```

Return n independent iterators from a single iterable.

The following Python code helps explain what tee does (although the actual implementation is more complex and uses only a single underlying FIFO queue).

Roughly equivalent to:

```Python
def tee(iterable, n=2):
    it = iter(iterable)
    deques = [collections.deque() for i in range(n)]
    def gen(mydeque):
        while True:
            if not mydeque:             # when the local deque is empty
                try:
                    newval = next(it)   # fetch a new value and
                except StopIteration:
                    return
                for d in deques:        # load it to all the deques
                    d.append(newval)
            yield mydeque.popleft()
    return tuple(gen(d) for d in deques)
```

Once tee() has made a split, the original iterable should not be used anywhere else; otherwise, the iterable could get advanced without the tee objects being informed.

tee iterators are not threadsafe. A RuntimeError may be raised when using simultaneously iterators returned by the same tee() call, even if the original iterable is threadsafe.

This itertool may require significant auxiliary storage (depending on how much temporary data needs to be stored). In general, if one iterator uses most or all of the data before another iterator starts, it is faster to use list() instead of tee().

### ```itertools.zip_longest(*iterables, fillvalue=None)```

Make an iterator that aggregates elements from each of the iterables. If the iterables are of uneven length, missing values are filled-in with fillvalue. Iteration continues until the longest iterable is exhausted. Roughly equivalent to:

```Python
def zip_longest(*args, fillvalue=None):
    # zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    iterators = [iter(it) for it in args]
    num_active = len(iterators)
    if not num_active:
        return
    while True:
        values = []
        for i, it in enumerate(iterators):
            try:
                value = next(it)
            except StopIteration:
                num_active -= 1
                if not num_active:
                    return
                iterators[i] = repeat(fillvalue)
                value = fillvalue
            values.append(value)
        yield tuple(values)
```

If one of the iterables is potentially infinite, then the zip_longest() function should be wrapped with something that limits the number of calls (for example islice() or takewhile()). If not specified, fillvalue defaults to None.

## Combinatoric Iterators

### ```itertools.product(*iterables, repeat=1)```

Cartesian product of input iterables.

Roughly equivalent to nested for-loops in a generator expression. For example, product(A, B) returns the same as ((x,y) for x in A for y in B).

The nested loops cycle like an odometer with the rightmost element advancing on every iteration. This pattern creates a lexicographic ordering so that if the input’s iterables are sorted, the product tuples are emitted in sorted order.

To compute the product of an iterable with itself, specify the number of repetitions with the optional repeat keyword argument. For example, product(A, repeat=4) means the same as product(A, A, A, A).

This function is roughly equivalent to the following code, except that the actual implementation does not build up intermediate results in memory:

```Python
def product(*args, repeat=1):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = [tuple(pool) for pool in args] * repeat
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
```

Before product() runs, it completely consumes the input iterables, keeping pools of values in memory to generate the products. Accordingly, it is only useful with finite inputs.

### ```itertools.permutations(iterable, r=None)```

Return successive r length permutations of elements in the iterable.

If r is not specified or is None, then r defaults to the length of the iterable and all possible full-length permutations are generated.

The permutation tuples are emitted in lexicographic ordering according to the order of the input iterable. So, if the input iterable is sorted, the combination tuples will be produced in sorted order.

Elements are treated as unique based on their position, not on their value. So if the input elements are unique, there will be no repeat values in each permutation.

Roughly equivalent to:

```Python
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return
```

The code for permutations() can be also expressed as a subsequence of product(), filtered to exclude entries with repeated elements (those from the same position in the input pool):

```Python
def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    for indices in product(range(n), repeat=r):
        if len(set(indices)) == r:
            yield tuple(pool[i] for i in indices)
```

The number of items returned is n! / (n-r)! when 0 <= r <= n or zero when r > n.

### ```itertools.combinations(iterable, r)```

Return r length subsequences of elements from the input iterable.

The combination tuples are emitted in lexicographic ordering according to the order of the input iterable. So, if the input iterable is sorted, the combination tuples will be produced in sorted order.

Elements are treated as unique based on their position, not on their value. So if the input elements are unique, there will be no repeat values in each combination.

Roughly equivalent to:

```Python
def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)
```

The code for combinations() can be also expressed as a subsequence of permutations() after filtering entries where the elements are not in sorted order (according to their position in the input pool):

```Python
def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in permutations(range(n), r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
```

The number of items returned is n! / r! / (n-r)! when 0 <= r <= n or zero when r > n.

### ```itertools.combinations_with_replacement(iterable, r)```

Return r length subsequences of elements from the input iterable allowing individual elements to be repeated more than once.

The combination tuples are emitted in lexicographic ordering according to the order of the input iterable. So, if the input iterable is sorted, the combination tuples will be produced in sorted order.

Elements are treated as unique based on their position, not on their value. So if the input elements are unique, the generated combinations will also be unique.

Roughly equivalent to:

```Python
def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)
```

The code for combinations_with_replacement() can be also expressed as a subsequence of product() after filtering entries where the elements are not in sorted order (according to their position in the input pool):

```Python
def combinations_with_replacement(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(range(n), repeat=r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
```

The number of items returned is (n+r-1)! / r! / (n-1)! when n > 0.

## Overview

![Itertools 1](ScreenshotsForNotes/Chapter5/InfiniteIterators.PNG)
![Itertools 2](ScreenshotsForNotes/Chapter5/IteratorsTerminatingOnTheShortestInputSequence.PNG)
![Itertools 3](ScreenshotsForNotes/Chapter5/CombinatoricIterators.PNG)

# 6. Matrix and Vector Computation

\-

# 7. Compiling to C

```>```

## Introduction

The easiest way to get yoru code to run faster is to make it do less work. Assuming you've already chosen good algorithms and you've reduced the amount of data yoou're processing, the easiset way to execute fewer instructions is to compile your code down to machine code.

Python offers a number of options for this, including pure C-based compiling approaches like Cython; LLVM-based compiling via Numba; and the replacement virtual machine PyPy, which includes a built-in just-in-time (JIT) compiler. You need to balance the requirements of code adaptability and team velocity when deciding which route to take.

Each of these tools adds a new dependency to your toolchain, and Cython requires you to write in a new language type (a hybrid of Python and C), which means you need a new skill. Cython's new language may hurt your team's velocity, as team memebers without knowledge of C may have trouble supporting this code; in practice, though, this is probably a minor concern, as you'll use Cython only in well-chosen, small regions of your code.

It is worth noting that performing CPU and memory profiling on your code will probably start you thinking about higher-level algorithmic optimizations that you might apply. These algorithmic changes (such as additional logic to avoid computations or caching to avoid recalculation) could help you avoid doing unnecessary work in your code, and Python's expressivitiy help you to spot these algorithmic opportunities.

## What sort of speed gains are possible ?

***Gains of an order of magnitude or more are quite possible if your problem yields to a compiled approach.***

Python code that tends to run faster after compiling is mathematical, and it has lots of loops that repeat the same operations many times. Inside these loops, you're probably making lots of temporary objects.

Code that calls out to external libraries (such as regular expresssions, string operations, and calls to database libraries) is unlikely to show any speedup after compiling. Programs that are I/O-bound are also unlikely to show significant speedups.

Similarly, if your Python code focuses on calling vectorized ```numpy```` routines, it may not run an yfaster after compilation - it'll run faster only if the code being compiled is mainly Python (and probably if it is mainly looping).

Overall, it is very unlikely that your compiled code will run any faster than a handcrafted C rountine, but it is also unlikely to run much slower. It is quite possible that the generated C code from your Python will run as fast as a handwritten C routine, unless the C coder has parcticularly good knowledge of ways to tune the C code to the target machine's architecture.

For math-focused code, it is possible that a handcoded Fortran routine will beat an equivalent C routine, but again, this probably requires expert-level knowledge. Overall, a compiled result (probably using Cython) will be as close to a handocded-in-C result as most programmers will need.

Keep the following diagram in mind when you profile and work on your algorithm. A small amount of work on understanding your code through profiling should enable you to make smarter choicse at an algorithmic level. After this, some focused work with a compiler should buy you an additional speedup. It will probably be possible to keep tewaking your algorithm, but don't be surprised to see increasingly small imporvements coming from increasingly large amounts of work on your part. Know when additional effort isn't useful.

![Profiling Diagram](ScreenshotsForNotes/Chapter7/profiling_diagram.PNG)

If you're dealing with Python code and batteries-included libraries without ```numpy```, Cython and PyPy are your main choices. If you're working with ```numpy```, Cython and Numba are the right choices. These tools all support Python 3.6+.

## JIT versus AOT compilers

By compiling AOT, you create a static library that's specialized to your machine. If you download ```numpy```, ```scipy```, or ```scikit-learn```, it will compile parts of the library using Cython on your machine (or you'll use a prebuilt compiled library, if you're using a distribution lke Continuum's Anaconda). By compiling ahead of use, you'll have a library that can instantly be used to work on solving your problem.

By compiling JIT, you don't have to do much (if any) work up front; you let the compiler step in to compile just the right parts of the code at the time of use. This means you have a "cold star" problem - if most of your program could be compiled and currently noen of it is, when you start running yoru code, it'll run very slowly while it compiles. If this happens every time you run a script and you run the script many times, this cost can become significant. PyPy suffers from this problem, so you may not want to use it for short but frequently running scripts.

The current state of affairs shows us that compiling ahead of time buys us the best speedups, but often this requires the most manual effort. Just-in-time compiling offers some impressive speedups with very little manual intervention, but it can also run into the problem just described. You'll ahve to consider these trade-offs when choosing the right technology for your problem.

## Why does type information help the code run faster?

Python is dynamically typed - a variable can refer to an object of any type, and any lline of code can change the type of the object that is referred to. This makes it difficult for the virtual machine to optimize how the code is executed at the machine code level, as it doesn't konw whcih fundamental datatype will be used for future operations. Keeping the code generic makes it run more slowly.

Inside Python, every fundamental object, such as an integer, will be wrapped up in a higher-level Python object (e.g., an ```int``` for an integer). The higher-level object has extra functions like ```__hash__``` to assist with storage and ```__str__``` for printing.

Inside a seciton of code that is CPU-bound, it is often the case that the types of variables do not change. This gives us an opportunity for static compilation and faster code execution.

If all we want are a lot of intermediate mathematical operations, we don't need the higher-level functions, and we may not need athe machinery for reference coutning either. We can drop down to the machine code level and do our calculations quickly using machine code and bytes, rather than manipulating gthe higher-level Python object, which involves greater overhead. To do this, we determine the types of our objects ahead of time so we can generate the correct C code.

## Using a C compiler

```gcc``` is a very good choice for most platforms; it is well supported and quite advanced. It is often possible to squeeze out more perfromance by using a tuned compiler (e.g., Inte'ls ```icc``` may produce faster code than ```gcc``` on Intel devices), but the cost is that you have to gain more domain knowledge and learn thow ot tune the lfags on the alternative compiler.

C and C++ are often used for static compilation rather than other languages like Fortran because of their ubiquity and the wide ragne of supporting libraries. The compiler and the converter, such as Cython, can study the annotated code to determine wheter static optimization steps (like inlining functions and unrolling loops) can be applied.

Aggressive analysis of the intermediate abstract syntax tree (performed by Numba and PyPy) provides opportunities to combine knowledge of Python'ws way of expressing things to inform the underlying compiler how best to take advantage of the patterns that have been seen.

## Cython

Cython is a compile rthat converts type-annotated Python into a compiled extension module. The type annotations are C-like.  This extension can be imported as a regular Python module using ```import```. Getting started is simple, but a learning curve must be climbed with each additional elvel of complexity and optimization.

With the OpenMP standard, it is possible to convert parallel poroblems into multiprocessing-aware modules that run on multiple CPUs on one machine. The threads are hidden from your Python code; they operate via the generate C code.

Cython is a fork of Pyrex that expands the capabilities beyond the original aims of Pyrex. LIbraires that use Cython include SciPy, scikit-learn, lxml, and ZeroMQ.

Cython can be used via a ```setup.py``` script to compile a module. It can also be used interactively in IPython via a "magic" command. Typically, the types are annotated by the developer. although some automated annotaiton is possible.

## Compiling a pure python version using cython

The easy way to being writing a compiled extension module involves three files. Using our Julia set as an example, they are as follows:

* The calling Python code ( the bulk of our Julai code from earlier )
* The function to be compiled in a new ```.pyx``` file
* A ```setup.py``` that contains the instructions for calling Cython to make the extension module

Using this approach, the ```setup.py``` script is called to use Cython to compile the ```.pyx``` file into a compiled module. On Unix-like systems, the compiled module will probably be a ```.so``` file; on Windows it should be a ```.pyd``` (DLL-like Pyton Library).

For the Julia example, we'll use the following:

* ```julia1.py``` to build the input lists and call the calculation function
* ```cythonfn.pyx```, which contains the CPU-bound function that we can annotate
* ```setup.py```, which contains the build instructions

The result of running ```setup.py``` is a module that can be imported. In our ```julia1.py``` script in the following example, we need only to make some tiny change to ```import``` the new module and call our function.

```Python
# Inside julia1.py
import cythonfn

def calc_pure_python(desired_width, max_iterations):
    start_time = time.time()
    output = ctyhonfn.calcualte_z(max_iterations, zs, cs)
    end_time = time.time()
    secs = end_time - start_time
    print(f"Took {secs:0.2f} seconds")
```

In the next example, we wil lstar twith a pure Python version without type annotations:

```Python
# cythonfn.pyx

def calculate_z(maxiter, zs, cs):
    """Calcualte output list using Julia update rule"""
    output = [0] * len(zs)
    for i in range(len(zs)):
        n = 0
        z = zs[i]
        c = cs[i]

        while n < maxiter and abs(z) < 2:
            z = z * z + c
            n += 1

        output[i] = n

    return output
```

The following ```setup.py``` script is short; it defines thow to convert ```cythonfn.pyx``` into ```calculate.so```:

```Python
from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "cythonfn.pyx",
        compiler_directives = {
            "language_level": "3"
        }
    )
)
```

When we run ```setup.py``` script with the argument ```build_ext```, Cython will look for ```cythonfn.pyx``` and built ```cythonfn.so```. The ```language_levle``` is hardcoded to 3 here to force Python 3.x support.

Remember that hits is a manual step - if you update your ```.pyx``` or ```setup.py``` and forget to rerun the build command, you won't have an updated ```.so``` module to import. If you're unsure whether you combipled the code, check the timestamp for the ```.so``` file. If in doubt, delete the generated C files and the ```.so``` file and build them again.

```bash
$ python setup.py build_ext --inplace
```

The ```--inplace``` argument tells Cython to build the compiled module into the current directory rather than into a separate *build* directory. After the build has completed, we'll have the intermediate ```cythonfn.c```, which is rather hard to read, along with ```cythonfn.so```.

## ```pyximport```

A simplifed build system has been introduced via ```pyximport```. If yoru code has a simple setup and doesn't require third-party modules, you may be able to do away with ```setup.py``` completely.

By importing ```pyximport``` as seen in the following example and calling ```install```, any subsequently imported ```.pyx``` file will be automatically compiled. This ```.pyx``` file can include annotations, or in this case, it can be the unannotated code. The result runs in 4.7 seconds, as before; the only differencei s that we didn't have to write a ```setup.py``` file:

```Python
import pyximport
pyximport.install(language_level=3)
import cythonfn  # as defined in setup.py
```

## Cython annotations to analyze a block of code

The preceding example shows that we can quickly build a compiled module. For tight loops and mathematical operations, this alone often leads to a speedup. Obviously, though, we should not optimize blindly—we need to know which lines of code take a lot of time so we can decide where to focus our efforts. Cython has an annotation option that will output an HTML file we can view in a browser. We use the command cython -a cythonfn.pyx, and the output file cythonfn.html is generated. Viewed in a browser, it looks something like the following figure:

![Generated Cython](ScreenshotsForNotes/Chapter7/generated_cython.PNG)

Each line can be expanded with a double-click to show the generated C code. More yellow means “more calls into the Python virtual machine,” while more white means “more non-Python C code.” The goal is to remove as many of the yellow lines as possible and end up with as much white as possible. Although “more yellow lines” means more calls into the virtual machine, this won’t necessarily cause your code to run slower. Each call into the virtual machine has a cost, but the cost of those calls will be significant only if the calls occur inside large loops. Calls outside large loops (for example, the line used to create output at the start of the function) are not expensive relative to the cost of the inner calculation loop. Don’t waste your time on the lines that don’t cause a slowdown. In our example, the lines with the most calls back into the Python virtual machine (the “most yellow”) are lines 4 and 8. From our previous profiling work, we know that line 8 is likely to be called over 30 million times, so that’s a great candidate to focus on. Lines 9, 10, and 11 are almost as yellow, and we also know they’re inside the tight inner loop. In total they’ll be responsible for the bulk of the execution time of this function, so we need to focus on these first. Refer back to “Using line_profiler for Line-by-Line Measurements” if you need to remind yourself of how much time is spent in this section. Lines 6 and 7 are less yellow, and since they’re called only 1 million times, they’ll have a much smaller effect on the final speed, so we can focus on them later. In fact, since they are list objects, there’s actually nothing we can do to speed up their access except, as you’ll see in “Cython and numpy”, to replace the list objects with numpy arrays, which will buy a small speed advantage. To better understand the yellow regions, you can expand each line. In the following figure, we can see that to create the output list, we iterate over the length of zs, building new Python objects that are reference-counted by the Python virtual machine. Even though these calls are expensive, they won’t really affect the execution time of this function. To improve the execution time of our function, we need to start declaring the types of objects that are involved in the expensive inner loops. These loops can then make fewer of the relatively expensive calls back into the Python virtual machine, saving us time. In general, the lines that probably cost the most CPU time are those:

* Inside tight inner loops
* Dereferencing ```list```, ```array```, or ```np.array``` items
* Performing mathematical operations

![Generated Cython](ScreenshotsForNotes/Chapter7/generated_cython_2.PNG)

If you don’t know which lines are most frequently executed, using a profiling tool—line_profiler, discussed in “Using line_profiler for Line-by-Line Measurements”, wouldbe the most appropriate. You’ll learn which lines are executed most frequently and whichlines cost the most inside the Python virtual machine, so you’ll have clear evidence of whichlines you need to focus on to get the best speed gain.

## Adding some type annotations

The first generated cython code in the first figure shows that almost every line of our function is calling back into thePython virtual machine. All of our numeric work is also calling back intoPython as we are using the higher-level Python objects. We need to convertthese into local C objects, and then, after doing our numerical coding, weneed to convert the result back to a Python object.

In the following example, we see how to add some primitive types by using the cdefsyntax.

It is important to note that these types will be understood only by Cython and not by Python.Cython uses these types to convert the Python code to C objects, which do not have to callback into the Python stack; this means the operations run at a faster speed, but they loseflexibility and development speed.

The types we add are as follows:

* int for a signed integer
* unsigned int for an integer that can only be positive
* double complex for double-precision complex numbers

The ```cdef``` keyword lets us declare variables inside the function body. Thesemust be declared at the top of the function, as that’s a requirement from the C language specification

```Python
def calculate_z(int maxiter, zs, cs):
    """Calculate output list using Julia update rule"""
    cdef unsigned int i, n
    cdef double complex z, c
    output = [0] * len(zs)
    for i in range(len(zs)):
        n = 0
        z = zs[i]
        c = cs[i]

        while n < maxiter and abs(z) < 2:
            z = z * z + c
            n += 1

        output[i] = n

    return output
```

When adding Cython annotations, you’re adding non-Python code to the .pyx file. This means you lose the interactive nature of developing Python in the interpreter. For those ofyou familiar with coding in C, we go back to the code-compile-run-debug cycle.

You might wonder if we could add a type annotation to the lists that we passin. We can use the list keyword, but this has no practical effect for this example. The list objects still have to be interrogated at the Python level topull out their contents, and this is very slow.

The act of giving types to some of the primitive objects is reflected in theannotated output in the following figure. Critically, lines 11 and 12—two of our mostfrequently called lines—have now turned from yellow to white, indicating thatthey no longer call back to the Python virtual machine. We can anticipate agreat speedup compared to the previous version.

![Generated Cython](ScreenshotsForNotes/Chapter7/generated_cython_3.PNG)

After compiling, this version takes 0.49 seconds to complete. With only a fewchanges to the function, we are running at 15 times the speed of the originalPython version.

It is important to note that the reason we are gaining speed is that more of thefrequently performed operations are being pushed down to the C level—inthis case, the updates to z and n. This means that the C compiler can optimize the way the lower-level functions are operating on the bytes thatrepresent these variables, without calling into the relatively slow Python virtual machine.

As noted earlier in this chapter, abs for a complex number involves taking the square root of the sum of the squares of the real and imaginary components. In our test, we want to see if the square root of the result is less than 2. Rather than taking the square root, we can instead square the other side of the comparison, so we turn < 2 into < 4. This avoids having to calculate the square root as the final part of the abs function.

In essence, we started with:

![math](ScreenshotsForNotes/Chapter7/math_example.PNG)

and we have simplified the operation to

![math](ScreenshotsForNotes/Chapter7/math_example_2.PNG)

If we retained the sqrt operation in the following code, we would still see an improvement in execution speed. One of the secrets to optimizing code is to make it do as little work as possible. Removing a relatively expensive operation by considering the ultimate aim of a function means that the C compiler can focus on what it is good at, rather than trying to intuit the programmer’s ultimate needs.

Writing equivalent but more specialized code to solve the same problem is known as strength reduction. You trade worse flexibility (and possibly worse readability) for faster execution.

This mathematical unwinding leads to the following example, in which we have replaced the relatively expensive abs function with a simplified line of expanded mathematics.

```Python
#cython: boundscheck=False
def calculate_z(int maxiter, zs, cs):
    """Calculate output list using Julia update rule"""
    cdef unsigned int i, n
    cdef double complex z, c
    output = [0] * len(zs)

    for i in range(len(zs)):
        n = 0
        z = zs[i]
        c = cs[i]

        while n < maxiter and (z.real * z.real + z.imag * z.imag) < 4:
            z = z * z + c
            n += 1

        output[i] = n

    return output
```

By annotating the code, we see that the while on line 10 (of the following figure) has become a little more yellow—it looks as though it might be doing more work rather than less. It isn’t immediately obvious how much of a speed gain we’ll get, but we know that this line is called over 30 million times, so we anticipate a good improvement.

This change has a dramatic effect—by reducing the number of Python calls in the innermost loop, we greatly reduce the calculation time of the function. This new version completes in just 0.19 seconds, an amazing 40× speedup over the original version. As ever, take a guide from what you see, but measure to test all of your changes.

![Generated Cython](ScreenshotsForNotes/Chapter7/generated_cython_4.PNG)

For a final possible improvement on this piece of code, we can disable bounds checking for each dereference in the list. The goal of the bounds checking is to ensure that the program does not access data outside the allocated array—in C it is easy to accidentally access memory outside the bounds of an array, and this will give unexpected results (and probably a segmentation fault!).

By default, Cython protects the developer from accidentally addressing outside the list’s limits. This protection costs a little bit of CPU time, but it occurs in the outer loop of our function, so in total it won’t account for much time. Disabling bounds checking is usually safe unless you are performing your own calculations for array addressing, in which case you will have to be careful to stay within the bounds of the list.

Cython has a set of flags that can be expressed in various ways. The easiest is to add them as single-line comments at the start of the .pyx file. It is also possible to use a decorator or compile-time flag to change these settings. To disable bounds checking, we add a directive for Cython inside a comment at the start of the .pyx file

```Python
#cython: boundscheck = False
def calculate_z(int maxiter, zs, cs):
```

## Numba

Numba from Continuum Analytics is a just-in-time compiler that specializes in numpy code, which it compiles via the LLVM compiler (not via g++ or gcc++, as used by our earlier examples) at runtime. It doesn’t require a precompilation pass, so when you run it against new code, it compiles each annotated function for your hardware. The beauty is that you provide a decorator telling it which functions to focus on and then you let Numba take over. It aims to run on all standard numpy code.

Numba is now fairly stable, so if you use numpy arrays and have nonvectorized code that iterates over many items, Numba should give you a quick and very painless win. Numba does not bind to external C libraries (which Cython can do), but it can automatically generate code for GPUs (which Cython cannot).

One drawback when using Numba is the toolchain—it uses LLVM, and this has many dependencies. We recommend that you use Continuum’s Anaconda distribution, as everything is provided; otherwise, getting Numba installed in a fresh environment can be a very time-consuming task.

The following example shows the addition of the @jit decorator to our core Julia function. This is all that’s required; the fact that numba has been imported means that the LLVM machinery kicks in at execution time to compile this function behind the scenes.

```Python
from numba import jit

@jit()
def calcualte_z_serial_purepython(maxiter, zs, cs, output):
```

If the @jit decorator is removed, this is just the numpy version of the Julia demo running with Python 3.7, and it takes 21 seconds. Adding the @jit decorator drops the execution time to 0.75 seconds. This is very close to the result we achieved with Cython, but without all of the annotation effort.

If we run the same function a second time in the same Python session, it runs even faster at 0.47 seconds—there’s no need to compile the target function on the second pass if the argument types are the same, so the overall execution speed is faster. On the second run, the Numba result is equivalent to the Cython with numpy result we obtained before (so it came out as fast as Cython for very little work!). PyPy has the same warm-up requirement.

If you’d like to read another view on what Numba offers, see “Numba”, where core developer Valentin Haenel talks about the @jit decorator, viewing the original Python source, and going further with parallel options and the typed List and typed Dict for pure Python compiled interoperability

## PyPy

PyPy is an alternative implementation of the Python language that includes a tracing just-in-time compiler; it is compatible with Python 3.5+. Typically, it lags behind the most recent version of Python; at the time of writing this second edition Python 3.7 is standard, and PyPy supports up to Python 3.6. PyPy is a drop-in replacement for CPython and offers all the built-in module s. The project comprises the RPython Translation Toolchain, which is used to build PyPy (and could be used to build other interpreters). The JIT compiler in PyPy is very effective, and good speedups can be seen with little or no work on your part.

PyPy runs our pure Python Julia demo without any modifications. With CPython it takes 8 seconds, and with PyPy it takes 0.9 seconds. This means that PyPy achieves a result that’s very close to the Cython example , without any effort at all—that’s pretty impressive! As we observed in our discussion of Numba, if the calculations are run again in the same session, then the second and subsequent runs are faster than the first one, as they are already compiled.

The fact that PyPy supports all the built-in modules is interesting—this means that multiprocessing works as it does in CPython. If you have a problem that runs with the batteries-included modules and can run in parallel with multiprocessing, you can expect that all the speed gains you might hope to get will be available.

PyPy’s speed has evolved over time. The older chart in the following figure (from speed.pypy.org) will give you an idea about PyPy’s maturity. These speed tests reflect a wide range of use cases, not just mathematical operations. It is clear that PyPy offers a faster experience than CPython.

![PyPy](ScreenshotsForNotes/Chapter7/pypy_chart.PNG)

### Garbage collection differences

PyPy uses a different type of garbage collector than CPython, and this can cause some nonobvious behavior changes to your code. Whereas CPython uses reference counting, PyPy uses a modified mark-and-sweep approach that may clean up an unused object much later. Both are correct implementations of the Python specification; you just have to be aware that code modifications might be required when swapping.

Some coding approaches seen in CPython depend on the behavior of the reference counter—particularly the flushing of files, if you open and write to them without an explicit file close. With PyPy the same code will run, but the updates to the file might get flushed to disk later, when the garbage collector next runs. An alternative form that works in both PyPy and Python is to use a context manager using with to open and automatically close files. The Differences Between PyPy and CPython page on the PyPy website lists the details.

## A summary of speed improvements

To summarize the previous results, in the first table we see that PyPy on a pure Python math-based code sample is approximately 9× faster than CPython with no code changes, and it’s even faster if the abs line is simplified. Cython runs faster than PyPy in both instances but requires annotated code, which increases development and support effort:

![Table](ScreenshotsForNotes/Chapter7/table1.PNG)

The Julia solver with numpy enables the investigation of OpenMP. In the next table, we see that both Cython and Numba run faster than the non-numpy versions with expanded math. When we add OpenMP, both Cython and Numba provide further speedups for very little additional coding

![Table](ScreenshotsForNotes/Chapter7/table2.PNG)

For pure Python code, PyPy is an obvious first choice. For ```numpy``` code, Numba is a great first choice.

## When to use each technology

If you're working on a numeric proejct, then each of these technoologies could be useful to you. The next table summarizes the main options.

![Table](ScreenshotsForNotes/Chapter7/table3.PNG)

## Graphics Processing Units (GPUs)

Graphics Processing Units (GPUs) are becoming incredibly popular as a method to speed up arithmetic-heavy computational workloads. Originally designed to help handle the heavy linear algebra requirements of 3D graphics, GPUs are particularly well suited for solving easily parallelizable problems.

Interestingly, GPUs themselves are slower than most CPUs if we just look at clock speeds. This may seem counterintuitive, but as we discussed in “Computing Units”, clock speed is just one measurement of hardware’s ability to compute. GPUs excel at massively parallelize tasks because of the staggering number of compute cores they have. CPUs generally have on the order of 12 cores, while modern-day GPUs have thousands.

## Basic GPU Profiling

One way to verify exactly how much of the GPU we are utilizing is by using the nvidia-smi command to inspect the resource utilization of the GPU. The two values we are most interested in are the power usage and the GPU utilization:

![GPU-PROFILING](ScreenshotsForNotes/Chapter7/gpu_profiling.PNG)

GPU utilization, here at 95%, is a slightly mislabeled field. It tells us what percentage of the last second has been spent running at least one kernel. So it isn’t telling us what percentage of the GPU’s total computational power we’re using but rather how much time was spent not being idle. This is a very useful measurement to look at when debugging memory transfer issues and making sure that the CPU is providing the GPU with enough work. Power usage, on the other hand, is a good proxy for judging how much of the GPU’s compute power is being used. As a rule of thumb, the more power the GPU is drawing, the more compute it is currently doing. If the GPU is waiting for data from the CPU or using only half of the available cores, power use will be reduced from the maximum.

Another useful tool is gpustat. This project provides a nice view into many of NVIDIA’s stats using a much friendlier interface than nvidia-smi.

## Performance considerations of GPUs

Since a GPU is a completely auxiliary piece of hardware on the computer, with its own architecture as compared with the CPU, there are many GPUspecific performance considerations to keep in mind.

The biggest speed consideration for GPUs is the transfer time of data from the system memory to the GPU memory.

GPUs are not particularly good at running multiple tasks at the same time. When starting up a task that requires heavy use of the GPU, ensure that no other tasks are utilizing it by running nvidia-smi. However, if you are running a graphical environment, you may have no choice but to have your desktop and GPU code use the GPU at the same time.

## When to use GPUs

We’ve seen that GPUs can be incredibly quick; however, memory considerations can be quite devastating to this runtime. This seems to indicate that if your task requires mainly linear algebra and matrix manipulations (like multiplication, addition, and Fourier transforms), then GPUs are a fantastic tool. This is particularly true if the calculation can 5 happen on the GPU uninterrupted for a period of time before being copied back into system memory.

In addition, because of the limited memory of the GPU, it is not a good tool for tasks that require exceedingly large amounts of data, many conditional manipulations of the data, or changing data. Most GPUs made for computational tasks have around 12 GB of memory, which puts a significant limitation on “large amounts of data.” However, as technology improves, the size of GPU memory increases, so hopefully this limitation becomes less drastic in the future.

The general recipe for evaluating whether to use the GPU consists of the following steps:

1. Ensure that the memory use of the problem will fit within the GPU (in “Using memory_profiler to Diagnose Memory Usage”, we explore profiling memory use).
2. Evaluate whether the algorithm requires a lot of branching conditions versus vectorized operations. As a rule of thumb, numpy functions generally vectorize very well, so if your algorithm can be written in terms of numpy calls, your code probably will vectorize well! You can also check the branches result when running perf (as explained in “Understanding perf”).
3. Evaluate how much data needs to be moved between the GPU and the CPU. Some questions to ask here are “How much computation can I do before I need to plot/save results?” and “Are there times my code will have to copy the data to run in a library I know isn’t GPUcompatible?”
4. Make sure PyTorch supports the operations you’d like to do! PyTorch implements a large portion of the numpy API, so this shouldn’t be an issue. For the most part, the API is even the same, so you don’t need to change your code at all. However, in some cases either PyTorch doesn’t support an operation (such as dealing with complex numbers) or the API is slightly different (for example, with generating random numbers).

Considering these four points will help give you confidence that a GPU approach would be worthwhile. There are no hard rules for when the GPU will work better than the CPU, but these questions will help you gain some intuition

## Foregin Function Interfaces

Sometimes the automatic solutions just don’t cut it, and you need to write custom C or Fortran code yourself. This could be because the compilation methods don’t find some potential optimizations, or because you want to take advantage of libraries or language features that aren’t available in Python. In all of these cases, you’ll need to use foreign function interfaces, which give you access to code written and compiled in another language.

### ```ctypes```

The most basic foreign function interface in CPython is through the ctypes module. The bare-bones nature of this module can be quite inhibitive at times—you are in charge of doing everything, and it can take quite a while to make sure that you have everything in order. This extra level of complexity is evident in our ctypes diffusion code, shown in the following example:

```Python
import ctypes
grid_shape = (512, 512)
_diffusion = ctypes.CDLL("diffusion.so")

# Create references to the C types that we will need to simplify future code
TYPE_INT = ctypes.c_int
TYPE_DOUBLE = ctypes.c_double
TYPE_DOUBLE_SS = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))

# Initialize the signature of the evolve function to:
# void evolve(int, int, double**, double**, double, double)
_diffusion.evolve.argtypes = [TYPE_DOUBLE_SS, TYPE_DOUBLE_SS, TYPE_DOUBLE,
TYPE_DOUBLE]
_diffusion.evolve.restype = None

def evolve(grid, out, dt, D=1.0):
    # First we convert the Python types into the relevant C types
    assert grid.shape == (512, 512)
    cdt = TYPE_DOUBLE(dt)
    cD = TYPE_DOUBLE(D)
    pointer_grid = grid.ctypes.data_as(TYPE_DOUBLE_SS)
    pointer_out = out.ctypes.data_as(TYPE_DOUBLE_SS)
    # Now we can call the function
    _diffusion.evolve(pointer_grid, pointer_out, cD, cdt)
```

This first thing we do is “import” our shared library. This is done with the ctypes.CDLL call. In this line, we can specify any shared library that Python can access (for example, the ctypes-opencv module loads the libcv.so library). From this, we get a _diffusion object that contains all the members that the shared library contains. In this example, diffusion.so contains only one function, evolve, which is now made available to us as a property of the _diffusion object. If diffusion.so had many functions and properties, we could access them all through the _diffusion object.

However, even though the _diffusion object has the evolve function available within it, Python doesn’t know how to use it. C is statically typed, and the function has a very specific signature. To properly work with the evolve function, we must explicitly set the input argument types and the return type. This can become quite tedious when developing libraries in tandem with the Python interface, or when dealing with a quickly changing library. Furthermore, since ctypes can’t check if you have given it the correct types, your code may silently fail or segfault if you make a mistake!

Furthermore, in addition to setting the arguments and return type of the function object, we also need to convert any data we care to use with it (this is called casting). Every argument we send to the function must be carefully casted into a native C type. Sometimes this can get quite tricky, since Python is very relaxed about its variable types. For example, if we had num1 = 1e5, we would have to know that this is a Python float, and thus we should use a ctype.c_float. On the other hand, for num2 = 1e300, we would have to use ctype.c_double, because it would overflow a standard C float.

That being said, numpy provides a .ctypes property to its arrays that makes it easily compatible with ctypes. If numpy didn’t provide this functionality, we would have had to initialize a ctypes array of the correct type and then find the location of our original data and have our new ctypes object point there.

Unless the object you are turning into a ctype object implements a buffer (as do the array module, numpy arrays, io.StringIO, etc.), your data will be copied into the new object. In the case of casting an int to a float, this doesn’t mean much for the performance of your code. However, if you are casting a very long Python list, this can incur quite a penalty! In these cases, using the array module or a numpy array, or even building up your own buffered object using the struct module, would help. This does, however, hurt the readability of your code, since these objects are generally less flexible than their native Python counterparts.

This memory management can get even more complicated if you have to send the library a complicated data structure. For example, if your library expects a C struct representing a point in space with the properties x and y, you would have to define the following:

```Python
from ctypes import Structure

class cPoint(Structure):
    _fields_ = ("x", c_int), ("y", c_int)
```

At this point you could start creating C-compatible objects by initializing a cPoint object (i.e., point = cPoint(10, 5)). This isn’t a terrible amount of work, but it can become tedious and results in some fragile code. What happens if a new version of the library is released that slightly changes the structure? This will make your code very hard to maintain and generally results in stagnant code, where the developers simply decide never to upgrade the underlying libraries that are being used.

For these reasons, using the ctypes module is great if you already have a good understanding of C and want to be able to tune every aspect of the interface. It has great portability since it is part of the standard library, and if your task is simple, it provides simple solutions. Just be careful because the complexity of ctypes solutions (and similar low-level solutions) quickly becomes unmanageable

### cffi

Realizing that ctypes can be quite cumbersome to use at times, cffi attempts to simplify many of the standard operations that programmers use. It does this by having an internal C parser that can understand function and structure definitions.

As a result, we can simply write the C code that defines the structure of the library we wish to use, and then cffi will do all the heavy work for us: it imports the module and makes sure we specify the correct types to the resulting functions. In fact, this work can be almost trivial if the source for the library is available, since the header files (the files ending in .h) will include all the relevant definitions we need. The following example shows the cffi version of the 2D diffusion code:

```Python
from cffi import FFI, verifier

grid_shape = (512, 512)

ffi = FFI()

ffi.cdef(
    "void evolve(double **in, double **out, double D, double dt);"
)
lib = ffi.dlopen("../diffusion.so")

def evolve(grid, dt, out, D=1.0):
    pointer_grid = ffi.cast("double**", grid.ctypes.data)
    pointer_out = ffi.cast("double**", out.ctypes.data)

    lib.evolve(pointer_grid, pointer_out, D, dt)
```

In the preceding code, we can think of the cffi initialization as being twostepped. First, we create an FFI object and give it all the global C declarations we need. This can include datatypes in addition to function signatures. These signatures don’t necessarily contain any code; they simply need to define what the code will look like. Then we can import a shared library containing the actual implementation of the functions by using dlopen. This means we could have told FFI about the function signature for the evolve function and then loaded up two different implantations and stored them in different objects (which is fantastic for debugging and profiling!).

In addition to easily importing a shared C library, cffi allows you to write C code and have it be dynamically compiled using the verify function. This has many immediate benefits—for example, you can easily rewrite small portions of your code to be in C without invoking the large machinery of a separate C library. Alternatively, if there is a library you wish to use, but some glue code in C is required to have the interface work perfectly, you can inline it into your cffi code, as shown in the following example, to have everything be in a centralized location. In addition, since the code is being dynamically compiled, you can specify compile instructions to every chunk of code you need to compile. Note, however, that this compilation has a one-time penalty every time the verify function is run to actually perform the compilation.

```Python
from cffi import FFI, verifier

grid_shape = (512, 512)

ffi = FFI()

ffi.cdef(
    "void evolve(double **in, double **out, double D, double dt);"
)
lib = ffi.dlopen("../diffusion.so")

lib = ffi.verify(
    r"""
        void evolve(double in[][512], double out[][512], double D, double dt) {
            int i, j;
            double laplacian;

            for(i = 1 ; i < 511; i++) {
                for (j = 1 ; j < 511;j++) {
                    laplacian = in[i+1][j] + in[i-1][j] + in[i][j+1] + in[i][j-1] - 4 * in[i][j];
                    out[i][j] = in[i][j] + D * dt * laplacian;
                }
            }
        }
    """,
    extra_compile_args = ["-03"]
)
```

Another benefit of the verify functionality is that it plays nicely with complicated cdef statements. For example, if we were using a library with a complicated structure but wanted to use only a part of it, we could use the partial struct definition. To do this, we add a ... in the struct definition in ffi.cdef and #include the relevant header file in a later verify.

For example, suppose we were working with a library with header complicated.h that included a structure that looked like this:

```Python
struct Point {
    double x;
    double y;
    bool isActive;
    char *id;
    int num_times_visited;
}
```

If we cared only about the ```x``` and ```y``` properties, we could write some simple ```cffi``` code that cares only about those values:

```Python
from cffi import FFI

ffi = FFI()
ffi.cdef(r"""
    struct Point {
        double x;
        double y;
        ...;
    };
    struct Point do_calculation();
""")

lib = ffi.verify(r"""
    #include <complicated.h>
""")
```

### CPython Module

Finally, we can always go right down to the CPython API level and write a CPython module. This requires us to write code in the same way that CPython is developed and take care of all of the interactions between our code and the implementation of CPython. This has the advantage that it is incredibly portable, depending on the Python version. We don’t require any external modules or libraries, just a C compiler and Python! However, this doesn’t necessarily scale well to new versions of Python. For example, CPython modules written for Python 2.7 won’t work with Python 3, and vice versa.

In fact, much of the slowdown in the Python 3 rollout was rooted in the difficulty in making this change. When creating a CPython module, you are coupled very closely to the actual Python implementation, and large changes in the language (such as the change from 2.7 to 3) require large modifications to your module.

That portability comes at a big cost, though—you are responsible for every aspect of the interface between your Python code and the module. This can make even the simplest tasks take dozens of lines of code.

All in all, this method should be left as a last resort. While it is quite informative to write a CPython module, the resulting code is not as reusable or maintainable as other potential methods. Making subtle changes in the module can often require completely reworking it. In fact, we include the module code and the required setup.py to compile it as a cautionary tale.

# 8. Asynchronous I/O

## Introduction

So far we have focused on speeding up code by increasing the number of compute cycles that a program can complete in a given time. However, in the days of big data, getting the relevant data to your code can be the bottleneck, as opposed to the actual code itself. When this is the case, your program is called I/O bound; in other words, the speed is bounded by the efficiency of the input/output.

I/O can be quite burdensome to the flow of a program. Every time your code reads from a file or writes to a network socket, it must pause to contact the kernel, request that the actual read happens, and then wait for it to complete. This is because it is not your program but the kernel that does the actual read operation, since the kernel is responsible for managing any interaction with hardware. The additional layer may not seem like the end of the world, especially once you realize that a similar operation happens every time memory is allocated; however we see that most of the I/O operations we perform are on devices that are orders of magnitude slower than the CPU. So even if the communication with the kernel is fast, we’ll be waiting quite some time for the kernel to get the result from the device and return it to us.

For example, in the time it takes to write to a network socket, an operation that typically takes about 1 millisecond, we could have completed 2,400,000 instructions on a 2.4 GHz computer. Worst of all, our program is halted for much of this 1 millisecond of time—our execution is paused, and then we wait for a signal that the write operation has completed. This time spent in a paused state is called I/O wait.

Asynchronous I/O helps us utilize this wasted time by allowing us to perform other operations while we are in the I/O wait state. For example, in Figure 8-1 we see a depiction of a program that must run three tasks, all of which have periods of I/O wait within them. If we run them serially, we suffer the I/O wait penalty three times. However, if we run these tasks concurrently, we can essentially hide the wait time by running another task in the meantime. It is important to note that this is all still happening on a single thread and still uses only one CPU at a time!

This is possible because while a program is in I/O wait, the kernel is simply waiting for whatever device we’ve requested to read from (hard drive, network adapter, GPU, etc.) to send a signal that the requested data is ready. Instead of waiting, we can create a mechanism (the event loop) so that we can dispatch requests for data, continue performing compute operations, and be notified when the data is ready to be read. This is in stark contrast to the multiprocessing/multithreading (Chapter 9) paradigm, where a new process is launched that does experience I/O wait but uses the multi-tasking nature of modern CPUs to allow the main process to continue. However, the two mechanisms are often used in tandem, where we launch multiple processes, each of which is efficient at asynchronous I/O, in order to fully take advantage of our computer’s resources.

Since concurrent programs run on a single thread, they are generally easier to write and manage than standard multithreaded programs. All concurrent functions share the same memory space, so sharing data between them works in the normal ways you would expect. However, you still need to be careful about race conditions since you can’t be sure which lines of code get run when.

By modeling a program in this event-driven way, we are able to take advantage of I/O wait to perform more operations on a single thread than would otherwise be possible

![Serial vs Concurrent Programs](ScreenshotsForNotes/Chapter8/serial_vs_concurrent_programs.PNG)

## Introduction to Asynchronous Programming

Typically, when a program enters I/O wait, the execution is paused so that the kernel can perform the low-level operations associated with the I/O request (this is called a context switch), and it is not resumed until the I/O operation is completed. Context switching is quite a heavy operation. It requires us to save the state of our program (losing any sort of caching we had at the CPU level) and give up the use of the CPU. Later, when we are allowed to run again, we must spend time reinitializing our program on the motherboard and getting ready to resume (of course, all this happens behind the scenes).

With concurrency, on the other hand, we typically have an event loop running that manages what gets to run in our program, and when. In essence, an event loop is simply a list of functions that need to be run. The function at the top of the list gets run, then the next, etc. The following example shows a simple example of an event loop

```python
from queue import Queue
from functools import partial

eventloop = None


class EventLoop(Queue):
    def start(self):
        while True:
            function = self.get()
            function()


def do_hello():
    global eventloop
    print("Hello")
    eventloop.put(do_world)


def do_world():
    global eventloop
    print("world")
    eventloop.put(do_hello)


if __name__ == '__main__':
    eventloop = EventLoop()
    eventloop.put(do_hello)
    eventloop.start()
```

This may not seem like a big change; however, we can couple event loops with asynchronous (async) I/O operations for massive gains when performing I/O tasks. In this example, the call eventloop.put(do_world) approximates an asynchronous call to the do_world function. This operation is called nonblocking, meaning it will return immediately but guarantee that do_world is called at some point later. Similarly, if this were a network write with an async function, it will return right away even though the write has not happened yet. When the write has completed, an event fires so our program knows about it.

Putting these two concepts together, we can have a program that, when an I/O operation is requested, runs other functions while waiting for the original I/O operation to complete. This essentially allows us to still do meaningful calculations when we otherwise would have been in I/O wait.

Switching from function to function does have a cost. The kernel must take the time to set up the function to be called in memory, and the state of our caches won’t be as predictable. It is because of this that concurrency gives the best results when your program has a lot of I/O wait—the cost associated with switching can be much less than what is gained by making use of I/O wait time.

Generally, programming using event loops can take two forms: callbacks or futures. In the callback paradigm, functions are called with an argument that is generally called the callback. Instead of the function returning its value, it calls the callback function with the value instead. This sets up long chains of functions that are called, with each function getting the result of the previous function in the chain (these chains are sometimes referred to as “callback hell”).

# 9. The multiprocessing Module

## Introduction

CPython doesn’t use multiple CPUs by default. This is partly because Python was designed back in a single-core era, and partly because parallelizing can actually be quite difficult to do efficiently. Python gives us the tools to do it but leaves us to make our own choices. It is painful to see your multicore machine using just one CPU on a long-running process, though, so in this chapter we’ll review ways of using all the machine’s cores at once.

We just mentioned CPython—the common implementation that we all use. Nothing in the Python language stops it from using multicore systems. CPython’s implementation cannot efficiently use multiple cores, but future implementations may not be bound by this restriction.

We live in a multicore world—4 cores are common in laptops, and 32-core desktop configurations are available. If your job can be split to run on multiple CPUs without too much engineering effort, this is a wise direction to consider.

When Python is used to parallelize a problem over a set of CPUs, you can expect up to an n-times (n×) speedup with n cores. If you have a quad-core machine and you can use all four cores for your task, it might run in a quarter of the original runtime. You are unlikely to see a greater than 4× speedup; in practice, you’ll probably see gains of 3–4×.

Each additional process will increase the communication overhead and decrease the available RAM, so you rarely get a full n-times speedup. Depending on which problem you are solving, the communication overhead can even get so large that you can see very significant slowdowns. These sorts of problems are often where the complexity lies for any sort of parallel programming and normally require a change in algorithm. This is why parallel programming is often considered an art.

If you’re not familiar with Amdahl’s law, it is worth doing some background reading. The law shows that if only a small part of your code can be parallelized, it doesn’t matter how many CPUs you throw at it; it still won’t run much faster overall. Even if a large fraction of your runtime could be parallelized, there’s a finite number of CPUs that can be used efficiently to make the overall process run faster before you get to a point of diminishing returns.

The multiprocessing module lets you use process- and thread-based parallel processing, share work over queues, and share data among processes. It is mostly focused on singlemachine multicore parallelism (there are better options for multimachine parallelism). A very common use is to parallelize a task over a set of processes for a CPU-bound problem. You might also use OpenMP to parallelize an I/O-bound problem, but as we saw in Chapter 8, there are better tools for this (e.g., the new asyncio module in Python 3 and tornado).

To parallelize your task, you have to think a little differently from the normal way of writing a serial process. You must also accept that debugging a parallelized task is harder—often, it can be very frustrating. We’d recommend keeping the parallelism as simple as possible (even if you’re not squeezing every last drop of power from your machine) so that your development velocity is kept high.

One particularly difficult topic is the sharing of state in a parallel system—it feels like it should be easy, but it incurs lots of overhead and can be hard to get right. There are many use cases, each with different trade-offs, so there’s definitely no one solution for everyone. In “Verifying Primes Using Interprocess Communication”, we’ll go through state sharing with an eye on the synchronization costs. Avoiding shared state will make your life far easier.

In fact, an algorithm can be analyzed to see how well it’ll perform in a parallel environment almost entirely by how much state must be shared. For example, if we can have multiple Python processes all solving the same problem without communicating with one another (a situation known as embarrassingly parallel), not much of a penalty will be incurred as we add more and more Python processes.

On the other hand, if each process needs to communicate with every other Python process, the communication overhead will slowly overwhelm the processing and slow things down. This means that as we add more and more Python processes, we can actually slow down our overall performance.

As a result, sometimes some counterintuitive algorithmic changes must be made to efficiently solve a problem in parallel. For example, when solving the diffusion equation (Chapter 6) in parallel, each process actually does some redundant work that another process also does. This redundancy reduces the amount of communication required and speeds up the overall calculation!

Here are some typical jobs for the multiprocessing module:

* Parallelize a CPU-bound task with Process or Pool objects
* Parallelize an I/O-bound task in a Pool with threads using the (oddly named) dummy module
* Share pickled work via a Queue
* Share state between parallelized workers, including bytes, primitive datatypes, dictionaries, and lists

If you come from a language where threads are used for CPUbound tasks (e.g., C++ or Java), you should know that while threads in Python are OS-native (they’re not simulated—they are actual operating system threads), they are bound by the GIL, so only one thread may interact with Python objects at a time.

By using processes, we run a number of Python interpreters in parallel, each with a private memory space with its own GIL, and each runs in series (so there’s no competition for each GIL). This is the easiest way to speed up a CPU-bound task in Python

## An overview of the multiprocessing module

The multiprocessing module provides a low-level interface to process- and thread-based parallelism. Its main components are as follows:

* Process
    * A forked copy of the current process; this creates a new process identifier, and the task runs as an independent child process in the operating system. You can start and query the state of the Process and provide it with a target method to run.
* Pool
    * Wraps the Process or threading.Thread API into a convenient pool of workers that share a chunk of work and return an aggregated result.
* Queue
    * A FIFO queue allowing multiple producers and consumers.
* Pipe
    * A uni- or bidirectional communication channel between two processes.
* Manager
    * A high-level managed interface to share Python objects between processes.
* ctypes
    * Allows sharing of primitive datatypes (e.g., integers, floats, and bytes) between processes after they have forked.
* Synchronization primitives
    * Locks and semaphores to synchronize control flow between processes

# 10. Clusters and Job Queues

## Introduction

A *cluster* is commonly recognized to be a collection of computers working togehter to solve a common task. It could be viewed from the outside as a larger single system.

Before you move to a clustered solution, do make sure that you have done the following:

* Profiled your system so you understand the bottlenecks
* Exploited compiler solutions like Numba and Cython
* Exploited multiple cores on a single machine (possibly a big machine with many cores) with Joblib or multiprocessing
* Exploited techniques for using less RAM

Keeping your system to one machine will make your life easier (even if the “one machine” is a really beefy computer with lots of RAM and many CPUs). Move to a cluster if you really need a lot of CPUs or the ability to process data from disks in parallel, or if you have production needs like high resiliency and rapid speed of response. Most research scenarios do not need resilience or scalability and are limited to few people, so the simplest solution is often the most sensible.

A benefit of staying on one large machine is that a tool like Dask can quickly parallelize your Pandas or plain Python code with no networking complications. Dask can also control a cluster of machines to parallelize Pandas, NumPy, and pure Python problems. Swifter automatically parallelizes some multicore single-machine cases by piggybacking on Dask. We introduce both Dask and Swifter later in this chapter.

## Benefits of Clustering

The most obvious benefit of a cluster is that you can easily scale computing requirements—if you need to process more data or to get an answer faster, you just add more machines (or nodes).

By adding machines, you can also improve reliability. Each machine’s components have a certain likelihood of failing, but with a good design, the failure of a number of components will not stop the operation of the cluster.

Clusters are also used to create systems that scale dynamically. A common use case is to cluster a set of servers that process web requests or associated data (e.g., resizing user photos, transcoding video, or transcribing speech) and to activate more servers as demand increases at certain times of the day.

Dynamic scaling is a very cost-effective way of dealing with nonuniform usage patterns, as long as the machine activation time is fast enough to deal with the speed of changing demand.

Consider the effort versus the reward of building a cluster. Whilst the parallelization gains of a cluster can feel attractive, do consider the costs associated with constructing and maintaining a cluster. They fit well for long-running processes in a production environment or for well-defined and oft-repeated R&D tasks. They are less attractive for variable and short-lived R&D tasks.

A subtler benefit of clustering is that clusters can be separated geographically but still centrally controlled. If one geographic area suffers an outage (due to a flood or power loss, for example), the other cluster can continue to work, perhaps with more processing units being added to handle the demand. Clusters also allow you to run heterogeneous software environments (e.g., different versions of operating systems and processing software), which might improve the robustness of the overall system—note, though, that this is definitely an expert-level topic!

## Drawbacks of Clustering

Moving to a clustered solution requires a change in thinking. This is an evolution of the change in thinking required when you move from serial to parallel code, as we introduced back in Chapter 9. Suddenly you have to consider what happens when you have more than one machine—you have latency between machines, you need to know if your other machines are working, and you need to keep all the machines running the same version of your software. System administration is probably your biggest challenge.

In addition, you normally have to think hard about the algorithms you are implementing and what happens once you have all these additional moving parts that may need to stay in sync. This additional planning can impose a heavy mental tax; it is likely to distract you from your core task, and once a system grows large enough, you’ll probably need to add a dedicated engineer to your team.

We’ve tried to focus on using one machine efficiently in this book because we believe that life is easier if you’re dealing with only one computer rather than a collection (though we confess it can be way more fun to play with a cluster—until it breaks). If you can scale vertically (by buying more RAM or more CPUs), it is worth investigating this approach in favor of clustering. Of course, your processing needs may exceed what’s possible with vertical scaling, or the robustness of a cluster may be more important than having a single machine. If you’re a single person working on this task, though, bear in mind also that running a cluster will suck up some of your time.

When designing a clustered solution, you’ll need to remember that each machine’s configuration might be different (each machine will have a different load and different local data). How will you get all the right data onto the machine that’s processing your job? Does the latency involved in moving the job and the data amount to a problem? Do your jobs need to communicate partial results to one another? What happens if a process fails or a machine dies or some hardware wipes itself when several jobs are running? Failures can be introduced if you don’t consider these questions.

You should also consider that failures can be acceptable. For example, you probably don’t need 99.999% reliability when you’re running a content-based web service—if on occasion a job fails (e.g., a picture doesn’t get resized quickly enough) and the user is required to reload a page, that’s something that everyone is already used to. It might not be the solution you want to give to the user, but accepting a little bit of failure typically reduces your engineering and management costs by a worthwhile margin. On the flip side, if a high-frequency trading system experiences failures, the cost of bad stock market trades could be considerable!

Maintaining a fixed infrastructure can become expensive. Machines are relatively cheap to purchase, but they have an awful habit of going wrong—automatic software upgrades can glitch, network cards fail, disks have write errors, power supplies can give spikey power that disrupts data, cosmic rays can flip a bit in a RAM module. The more computers you have, the more time will be lost to dealing with these issues. Sooner or later you’ll want to bring in a system engineer who can deal with these problems, so add another $100,000 to the budget. Using a cloud-based cluster can mitigate a lot of these problems (it costs more, but you don’t have to deal with the hardware maintenance), and some cloud providers also offer a spot-priced market for cheap but temporary computing resources.

An insidious problem with a cluster that grows organically over time is that it’s possible no one has documented how to restart it safely if everything gets turned off. If you don’t have a documented restart plan, you should assume you’ll have to write one at the worst possible time (one of your authors has been involved in debugging this sort of problem on Christmas Eve—this is not the Christmas present you want!). At this point you’ll also learn just how long it can take each part of a system to get up to speed—it might take minutes for each part of a cluster to boot and to start to process jobs, so if you have 10 parts that operate in succession, it might take an hour to get the whole system running from cold. The consequence is that you might have an hour’s worth of backlogged data. Do you then have the necessary capacity to deal with this backlog in a timely fashion?

Slack behavior can be a cause of expensive mistakes, and complex and hard-to-anticipate behavior can cause unexpected and expensive outcomes

## Common Clusters Designs

It is common to start with a local ad hoc cluster of reasonably equivalent machines. You might wonder if you can add old computers to an ad hoc network, but typically older CPUs eat a lot of power and run very slowly, so they don’t contribute nearly as much as you might hope compared to one new, highspecification machine. An in-office cluster requires someone who can maintain it. A cluster on Amazon’s EC2 or Microsoft’s Azure, or one run by an academic institution, offloads the hardware support to the provider’s team.

If you have well-understood processing requirements, it might make sense to design a custom cluster—perhaps one that uses an InfiniBand high-speed interconnect in place of gigabit Ethernet, or one that uses a particular configuration of RAID drives that support your read, write, or resiliency requirements. You might want to combine CPUs and GPUs on some machines, or just default to CPUs.

You might want a massively decentralized processing cluster, like the ones used by projects such as SETI@home and Folding@home through the Berkeley Open Infrastructure for Network Computing (BOINC) system. They share a centralized coordination system, but the computing nodes join and leave the project in an ad hoc fashion.

On top of the hardware design, you can run different software architectures. Queues of work are the most common and easiest to understand. Typically, jobs are put onto a queue and consumed by a processor. The result of the processing might go onto another queue for further processing, or it might be used as a final result (e.g., being added into a database). Message-passing systems are slightly different—messages get put onto a message bus and are then consumed by other machines. The messages might time out and get deleted, and they might be consumed by multiple machines. In a more complex system, processes talk to each other using interprocess communication—this can be considered an expert-level configuration, as there are lots of ways that you can set it up badly, which will result in you losing your sanity. Go down the IPC route only if you really know that you need it.

## How to start a clustered solution

The easiest way to start a clustered system is to begin with one machine that will run both the job server and a job processor (just one job processor for one CPU). If your tasks are CPUbound, run one job processor per CPU; if your tasks are I/Obound, run several per CPU. If they’re RAM-bound, be careful that you don’t run out of RAM. Get your single-machine solution working with one processor and then add more. Make your code fail in unpredictable ways (e.g., do a 1/0 in your code, use kill -9 <pid> on your worker, pull the power plug from the socket so the whole machine dies) to check if your system is robust.

Obviously, you’ll want to do heavier testing than this—a unit test suite full of coding errors and artificial exceptions is good. Ian likes to throw in unexpected events, like having a processor run a set of jobs while an external process is systematically killing important processes and confirming that these all get restarted cleanly by whatever monitoring process is being used.

Once you have one running job processor, add a second. Check that you’re not using too much RAM. Do you process jobs twice as fast as before?

Now introduce a second machine, with just one job processor on that new machine and no job processors on the coordinating machine. Does it process jobs as fast as when you had the processor on the coordinating machine? If not, why not? Is latency a problem? Do you have different configurations? Maybe you have different machine hardware, like CPUs, RAM, and cache sizes?

Now add another nine computers and test to see if you’re processing jobs 10 times faster than before. If not, why not? Are network collisions now occurring that slow down your overall processing rate?

To reliably start the cluster’s components when the machine boots, we tend to use either a cron job, Circus, or supervisord. Circus and supervisord are both Pythonbased and have been around for years. cron is old but very reliable if you’re just starting scripts like a monitoring process that can start subprocesses as required.

Once you have a reliable cluster, you might want to introduce a random-killer tool like Netflix’s Chaos Monkey, which deliberately kills parts of your system to test them for resiliency. Your processes and your hardware will die eventually, and it doesn’t hurt to know that you’re likely to survive at least the errors you predict might happen