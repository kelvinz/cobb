# Smell Baseline

Load this reference from `review` step 4 when the diff adds or changes logic beyond configuration, documentation, or generated output.

The baseline is a fixed set of Fowler code smells (*Refactoring*, chapter 3) that applies even when the repository documents no coding standards. Two rules bind it:

- **The repository overrides.** A documented repository standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy") reported as a suggestion, never a blocker on its own. Skip anything tooling already enforces.

Each smell reads *what it is* then *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name hides what it does or holds. Rename it; if no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape in more than one hunk or file of the change. Extract the shared shape and call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. Move the method onto the data it envies.
- **Data Clumps**: the same few fields or parameters travelling together. Bundle them into one type and pass that.
- **Primitive Obsession**: a primitive standing in for a domain concept that deserves its own type. Give the concept its own small type.
- **Repeated Switches**: the same switch or if-cascade on the same type recurring across the change. Replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forcing scattered edits across many files. Gather what changes together into one module.
- **Divergent Change**: one module edited for several unrelated reasons. Split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the PRD does not have. Delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller should not depend on. Hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly delegates onward. Cut it and call the real target directly.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. Drop the inheritance and use composition.

Report each match as `S#` with the smell name, the quoted hunk, and the concrete improvement.
