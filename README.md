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