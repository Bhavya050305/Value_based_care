from load_data import load_aco_data
from peer_model import train_and_save


if __name__ == "__main__":

    print("Loading ACO data from Supabase...")

    df = load_aco_data()

    print()
    print("Dataset loaded successfully.")
    print("Shape:", df.shape)

    train_and_save(df)