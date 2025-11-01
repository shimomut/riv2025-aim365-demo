#!/usr/bin/env python3
"""
HyperPod Cluster Testing Framework
"""

import subprocess
import time
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple


class HyperPodTester:
    def __init__(self, job_name: str = "llama3-1-8b-fsdp-hpto"):
        self.job_name = job_name
        self.namespace = "default"
        
    def run_kubectl_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Execute kubectl command and return success status and output."""
        try:
            result = subprocess.run(
                ["kubectl"] + cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Command failed: {str(e)}"
    
    def check_cluster_connectivity(self) -> bool:
        """Verify kubectl can connect to the cluster."""
        print("🔍 Checking cluster connectivity...")
        success, output = self.run_kubectl_command(["cluster-info"])
        if success:
            print("✅ Cluster connectivity verified")
            return True
        else:
            print(f"❌ Cluster connectivity failed: {output}")
            return False
    
    def check_hyperpod_operator(self) -> bool:
        """Verify HyperPod Training Operator is running."""
        print("🔍 Checking HyperPod Training Operator...")
        success, output = self.run_kubectl_command([
            "get", "pods", "-n", "kubeflow", 
            "-l", "app=training-operator"
        ])
        if success and "Running" in output:
            print("✅ HyperPod Training Operator is running")
            return True
        else:
            print(f"❌ HyperPod Training Operator not found: {output}")
            return False 
   
    def check_gpu_nodes(self) -> bool:
        """Check for available GPU nodes."""
        print("🔍 Checking GPU node availability...")
        success, output = self.run_kubectl_command([
            "get", "nodes", "-l", "sagemaker.amazonaws.com/compute-type", "-o", "wide"
        ])
        if success:
            lines = output.strip().split('\n')
            gpu_nodes = [line for line in lines if 'Ready' in line]
            if gpu_nodes:
                print(f"✅ Found {len(gpu_nodes)} GPU nodes ready")
                return True
            else:
                print("❌ No GPU nodes in Ready state")
                return False
        else:
            print(f"❌ Failed to check GPU nodes: {output}")
            return False
    
    def check_storage_claims(self) -> bool:
        """Verify FSx storage claims are bound."""
        print("🔍 Checking storage claims...")
        success, output = self.run_kubectl_command(["get", "pvc", "fsx-claim"])
        if success and "Bound" in output:
            print("✅ FSx storage claim is bound")
            return True
        else:
            print(f"❌ FSx storage claim not bound: {output}")
            return False
    
    def deploy_job(self) -> bool:
        """Deploy the FSDP training job."""
        print(f"🚀 Deploying job: {self.job_name}")
        success, output = self.run_kubectl_command([
            "apply", "-f", "FSDP/kubernetes/fsdp-hpto.yaml"
        ])
        if success:
            print("✅ Job deployed successfully")
            return True
        else:
            print(f"❌ Job deployment failed: {output}")
            return False
    
    def wait_for_job_start(self, timeout: int = 300) -> bool:
        """Wait for job pods to start running."""
        print(f"⏳ Waiting for job pods to start (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            success, output = self.run_kubectl_command([
                "get", "pods", "-l", f"job-name={self.job_name}"
            ])
            
            if success:
                lines = output.strip().split('\n')[1:]  # Skip header
                if lines and lines[0]:
                    running_pods = [line for line in lines if 'Running' in line]
                    total_pods = len(lines)
                    
                    print(f"📊 Pods status: {len(running_pods)}/{total_pods} running")
                    
                    if len(running_pods) == total_pods and total_pods > 0:
                        print("✅ All pods are running")
                        return True
            
            time.sleep(10)
        
        print("❌ Timeout waiting for pods to start")
        return False    

    def get_job_status(self) -> Dict:
        """Get detailed job status."""
        print("📊 Getting job status...")
        
        success, job_output = self.run_kubectl_command([
            "get", "hyperpodpytorchjob", self.job_name, "-o", "json"
        ])
        
        success_pods, pods_output = self.run_kubectl_command([
            "get", "pods", "-l", f"job-name={self.job_name}", "-o", "wide"
        ])
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "job_exists": success,
            "pods_info": pods_output if success_pods else "Failed to get pods"
        }
        
        if success:
            try:
                job_data = json.loads(job_output)
                status["job_status"] = job_data.get("status", {})
            except json.JSONDecodeError:
                status["job_status"] = "Failed to parse job status"
        
        return status
    
    def get_training_logs(self, lines: int = 50) -> str:
        """Get recent training logs from the first pod."""
        print(f"📋 Getting training logs (last {lines} lines)...")
        
        success, output = self.run_kubectl_command([
            "get", "pods", "-l", f"job-name={self.job_name}",
            "-o", "jsonpath={.items[0].metadata.name}"
        ])
        
        if not success or not output.strip():
            return "No pods found"
        
        pod_name = output.strip()
        success, logs = self.run_kubectl_command([
            "logs", pod_name, "--tail", str(lines)
        ])
        
        return logs if success else f"Failed to get logs: {logs}"
    
    def monitor_training_progress(self, duration: int = 300) -> None:
        """Monitor training progress for specified duration."""
        print(f"👀 Monitoring training progress for {duration} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            logs = self.get_training_logs(lines=10)
            
            loss_lines = [line for line in logs.split('\n') if 'Loss:' in line]
            if loss_lines:
                print(f"📈 Latest training update: {loss_lines[-1].strip()}")
            
            status = self.get_job_status()
            pods_info = status.get("pods_info", "")
            running_count = pods_info.count("Running")
            
            print(f"🔄 Pods running: {running_count}")
            
            time.sleep(30) 
   
    def cleanup_job(self) -> bool:
        """Clean up the training job."""
        print(f"🧹 Cleaning up job: {self.job_name}")
        success, output = self.run_kubectl_command([
            "delete", "-f", "FSDP/kubernetes/fsdp-hpto.yaml"
        ])
        
        if success:
            print("✅ Job cleanup completed")
            return True
        else:
            print(f"❌ Job cleanup failed: {output}")
            return False
    
    def run_full_test(self, monitor_duration: int = 300) -> bool:
        """Run complete test suite."""
        print("🧪 Starting HyperPod FSDP Training Test Suite")
        print("=" * 60)
        
        checks = [
            ("Cluster Connectivity", self.check_cluster_connectivity),
            ("HyperPod Operator", self.check_hyperpod_operator),
            ("GPU Nodes", self.check_gpu_nodes),
            ("Storage Claims", self.check_storage_claims),
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                print(f"❌ Pre-deployment check failed: {check_name}")
                return False
        
        print("✅ All pre-deployment checks passed")
        print("-" * 60)
        
        try:
            if not self.deploy_job():
                return False
            
            if not self.wait_for_job_start():
                print("⚠️  Job failed to start properly, checking status...")
                status = self.get_job_status()
                print(json.dumps(status, indent=2))
                return False
            
            self.monitor_training_progress(duration=monitor_duration)
            
            print("-" * 60)
            print("📊 Final Job Status:")
            status = self.get_job_status()
            print(json.dumps(status, indent=2))
            
            return True
            
        finally:
            self.cleanup_job()


def main():
    parser = argparse.ArgumentParser(description="HyperPod FSDP Training Test Suite")
    parser.add_argument("--job-name", default="llama3-1-8b-fsdp-hpto")
    parser.add_argument("--monitor-duration", type=int, default=300)
    parser.add_argument("--action", choices=["full-test", "status", "logs", "cleanup"],
                       default="full-test")
    
    args = parser.parse_args()
    tester = HyperPodTester(job_name=args.job_name)
    
    if args.action == "full-test":
        success = tester.run_full_test(monitor_duration=args.monitor_duration)
        sys.exit(0 if success else 1)
    elif args.action == "status":
        status = tester.get_job_status()
        print(json.dumps(status, indent=2))
    elif args.action == "logs":
        logs = tester.get_training_logs()
        print(logs)
    elif args.action == "cleanup":
        tester.cleanup_job()


if __name__ == "__main__":
    main()