from neurosymbolic.neural_ode import NeuralODEModel, generate_harmonic_oscillator


def test_neural_ode_harmonic_loss_decreases_quickly():
    t, trajectory = generate_harmonic_oscillator(n_steps=40, dt=0.04)
    model = NeuralODEModel(input_dim=2, hidden_dim=16, num_layers=1)

    losses = model.fit(t, trajectory, epochs=20, lr=0.02)

    assert losses[-1] < losses[0]
