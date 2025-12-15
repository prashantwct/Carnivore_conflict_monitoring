import React from 'react';
import { SafeAreaView, Text, StyleSheet, View } from 'react-native';

const App = () => {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tiger Reporter App</Text>
      </View>
      <View style={styles.content}>
        <Text style={styles.statusText}>Status: Ready for Login</Text>
        <Text style={styles.instruction}>
          To begin, integrate with the Backend API (http://localhost:5000/api/v1).
        </Text>
        {/* TODO: Implement Login and Incident Reporting Screens */}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a361c',
  },
  header: {
    padding: 20,
    backgroundColor: '#2e7d32',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 18,
    color: '#a5d6a7',
    marginBottom: 10,
  },
  instruction: {
    fontSize: 16,
    color: '#c8e6c9',
    textAlign: 'center',
    marginTop: 10,
  }
});

export default App;
