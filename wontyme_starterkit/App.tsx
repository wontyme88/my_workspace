import { useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { askClaude } from './lib/claude';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    if (!prompt.trim()) return;
    setLoading(true);
    setResponse('');
    try {
      const result = await askClaude(prompt);
      setResponse(result);
    } catch (e) {
      setResponse('Error: ' + (e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>wontyme starter</Text>
      <TextInput
        style={styles.input}
        placeholder="Claude에게 물어보세요"
        value={prompt}
        onChangeText={setPrompt}
        multiline
      />
      <TouchableOpacity style={styles.button} onPress={handleAsk} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>물어보기</Text>}
      </TouchableOpacity>
      {response ? <Text style={styles.response}>{response}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, paddingTop: 80, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 24 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, minHeight: 80, marginBottom: 12, fontSize: 16 },
  button: { backgroundColor: '#6c47ff', borderRadius: 8, padding: 14, alignItems: 'center', marginBottom: 16 },
  buttonText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  response: { fontSize: 15, lineHeight: 22, color: '#333' },
});
